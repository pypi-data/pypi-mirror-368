from fastapi import Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from svc_order_zxw.db import get_db
from svc_order_zxw.db.crud2_products import get_product
from svc_order_zxw.db.crud3_orders import (
    create_order,
    PYD_OrderCreate,
)
from svc_order_zxw.db.crud4_payments import (
    create_payment,
    PYD_PaymentCreate,
)
from svc_order_zxw.异常代码 import 商品_异常代码
from svc_order_zxw.apis.schemas_payments import OrderStatus, PaymentMethod
from svc_order_zxw.apis.func_生成订单号 import 生成订单号
from app_tools_zxw.Errors.api_errors import HTTPException_AppToolsSZXW
from app_tools_zxw.Funcs.fastapi_logger import setup_logger

logger = setup_logger(__name__)


class Model创建订单返回值(BaseModel):
    user_id: int
    product_id: int
    order_number: str

    total_price: float  # 原始价格
    payment_price: float  # 实际支付金额
    quantity: int
    status: str


async def 创建新订单_并创建支付单(
        user_id: int,
        product_id: int,
        payment_price: float,
        payment_method: PaymentMethod,
        quantity: int = 1,
        callback_url: str | None = None,
        payment_url: str | None = None,
        db_payment: AsyncSession = Depends(get_db)
):
    # 验证产品是否存在
    product = await get_product(db_payment, product_id)
    if not product:
        raise HTTPException_AppToolsSZXW(
            error_code=商品_异常代码.商品不存在.value,
            detail="商品不存在",
            http_status_code=404
        )

    # 创建新订单
    new_order = await create_order(db_payment, PYD_OrderCreate(
        order_number=生成订单号(),
        user_id=user_id,
        total_price=product.price * quantity,
        quantity=quantity,
        product_id=product_id,
    ))

    # 创建支付单
    new_payment = await create_payment(db_payment, PYD_PaymentCreate(
        order_id=new_order.id,
        payment_price=payment_price,
        payment_method=payment_method,
        payment_status=OrderStatus.PENDING,
        callback_url=callback_url,
        payment_url=payment_url,
    ))

    return Model创建订单返回值(
        order_number=new_order.order_number,
        user_id=new_order.user_id,
        product_id=new_order.product_id,
        total_price=new_order.total_price,
        payment_price=new_payment.payment_price,
        quantity=new_order.quantity,
        status=new_payment.payment_status.value
    )
