/**
 * 苹果内购 API 接口
 * 对接后端 api_IAP订单管理.py
 */

// UniApp 全局对象声明
declare const uni: any

// 基础配置
const BASE_URL = 'https://your-api-domain.com/apple_pay' // 替换为实际的API域名

// 请求类型定义
export interface CreateOrderRequest {
  user_id: string
  apple_product_id: string
  payment_price: number
  quantity?: number
  transactionIdentifier: string
  transactionReceipt: string
}

export interface RestoreSubscriptionRequest {
  user_id: string
  transactionIdentifier: string
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

// 基础请求函数
async function request(url: string, method: string, data?: any): Promise<any> {
  return new Promise((resolve, reject) => {
    uni.request({
      url: `${BASE_URL}${url}`,
      method: method as any,
      data,
      header: {
        'Content-Type': 'application/json'
      },
      success: (res) => {
        if (res.statusCode === 200) {
          resolve(res.data)
        } else {
          reject(new Error(`请求失败: ${res.statusCode}`))
        }
      },
      fail: (err) => {
        reject(err)
      }
    })
  })
}

// API 接口函数
export const applePayApi = {
  /**
   * 创建苹果内购订单
   */
  async createOrder(params: CreateOrderRequest): Promise<PaymentInfo> {
    return await request('/create_order', 'POST', params)
  },

  /**
   * 恢复购买
   */
  async restoreSubscription(params: RestoreSubscriptionRequest): Promise<PaymentInfo> {
    return await request('/restore_subscription', 'POST', params)
  }
}