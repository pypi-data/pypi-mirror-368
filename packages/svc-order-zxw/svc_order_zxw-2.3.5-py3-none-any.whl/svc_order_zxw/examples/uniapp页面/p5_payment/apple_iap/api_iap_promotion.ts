/**
 * 苹果内购优惠券管理 API 接口
 * 对接后端 api_IAP优惠券管理.py
 */

// UniApp 全局对象声明
declare const uni: any

// 基础配置
const BASE_URL = 'https://your-api-domain.com' // 替换为实际的API域名

// 请求类型定义
export interface CreatePromotionRequest {
  username: string
  apple_product_id: string
  subscription_offer_id: string
}

// 响应类型定义
export interface PromotionSignatureResult {
  product_id: string
  subscription_offer_id: string
  application_username: string
  nonce: string
  timestamp: number
  signature: string
  created_at: string
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
export const iapPromotionApi = {
  /**
   * 创建苹果内购优惠券签名
   * @param params 创建参数
   * @returns Promise<PromotionSignatureResult>
   */
  async createPromotion(params: CreatePromotionRequest): Promise<PromotionSignatureResult> {
    return await request('/iap/promotion/create', 'POST', params)
  }
}

// 导出默认对象
export default iapPromotionApi