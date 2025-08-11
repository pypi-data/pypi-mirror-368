/**
 * 苹果内购 API 接口
 * 对接后端 api_IAP订单管理.py
 */
import { buildApiUrl } from "@/config"
import { request } from "@/src/utils/request/request"


// 基础配置
const BASE_URL = buildApiUrl('/order_center/apple_pay') // 替换为实际的API域名

// 请求类型定义
export interface CreateOrderRequest {
  user_id: string
  product_id: number
  // apple_product_id: string
  payment_price: number
  quantity?: number
  transactionIdentifier?: string
  transactionReceipt?: string
}

export interface RestoreSubscriptionRequest {
  user_id: string
  product_id: number
  transactionIdentifier: string
  transactionReceipt:string
  apple_product_id: string
}

// 响应类型定义
export interface PaymentInfo {
  order_number: string
  payment_status: string
  payment_price: number
  quantity: number
  order_id: number
  product_name: string
  app_name: string
  transaction_id?: string
  original_transaction_id?: string
  subscription_expire_date?: string
  payment_method?: string
}

// API 接口函数
export const applePayApi = {
  /**
   * 创建苹果内购订单
   */
  async createOrder(params: CreateOrderRequest): Promise<PaymentInfo> {
    return await request({
      url: BASE_URL + '/create_order',
      method: 'POST',
      data: params,
      header: {
        'Content-Type': 'application/json'
      }
    }) as PaymentInfo
  },

  /**
   * 恢复购买
   */
  async restoreSubscription(params: RestoreSubscriptionRequest): Promise<PaymentInfo> {
    return await request({
      url: BASE_URL + '/restore_subscription',
      method: 'POST',
      data: params,
      header: {
        'Content-Type': 'application/json'
      }
    }) as PaymentInfo
  }
}