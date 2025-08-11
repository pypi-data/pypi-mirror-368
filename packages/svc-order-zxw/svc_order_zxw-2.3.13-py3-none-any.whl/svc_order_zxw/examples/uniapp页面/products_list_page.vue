<template>
  <view class="products-container">
    <!-- 头部筛选区域 -->
    <view class="filter-section">
      <view class="filter-item">
        <text class="filter-label">应用名称:</text>
        <input 
          v-model="queryParams.app_name" 
          placeholder="请输入应用名称"
          class="filter-input"
        />
      </view>
      
      <view class="filter-item">
        <text class="filter-label">商品类型:</text>
        <picker 
          :value="productTypeIndex" 
          :range="productTypes" 
          @change="onProductTypeChange"
          class="filter-picker"
        >
          <view class="picker-display">{{ productTypes[productTypeIndex] }}</view>
        </picker>
      </view>
      
      <button @click="loadProducts" class="search-btn" :loading="loading">
        {{ loading ? '查询中...' : '查询商品' }}
      </button>
    </view>

    <!-- 商品列表 -->
    <view class="products-list">
      <view v-if="products.length === 0 && !loading" class="empty-state">
        <text>暂无商品数据</text>
      </view>
      
      <view 
        v-for="product in products" 
        :key="product.id" 
        class="product-item"
        @click="onProductClick(product)"
      >
        <view class="product-header">
          <text class="product-name">{{ product.product_name }}</text>
          <text class="product-price">¥{{ product.price }}</text>
        </view>
        
        <view class="product-info">
          <text class="product-description">{{ product.product_description || '暂无描述' }}</text>
        </view>
        
        <view class="product-tags">
          <text class="tag" :class="{ 'apple-tag': product.is_apple_product }">
            {{ product.is_apple_product ? '苹果商品' : '普通商品' }}
          </text>
          <text class="tag" :class="{ 'active-tag': product.is_active }">
            {{ product.is_active ? '已上架' : '已下架' }}
          </text>
          <text class="app-tag">{{ product.app_name }}</text>
        </view>
      </view>
    </view>

    <!-- 加载更多 -->
    <view v-if="products.length > 0" class="load-more">
      <button 
        @click="loadMoreProducts" 
        class="load-more-btn"
        :loading="loadingMore"
        :disabled="!hasMore"
      >
        {{ loadingMore ? '加载中...' : hasMore ? '加载更多' : '没有更多了' }}
      </button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { productsApi, type ProductInfo, type GetProductsParams } from './api_products_query'

// 响应式数据
const products = ref<ProductInfo[]>([])
const loading = ref(false)
const loadingMore = ref(false)
const hasMore = ref(true)

// 查询参数
const queryParams = reactive<GetProductsParams>({
  app_name: '',
  is_apple_product: false,
  skip: 0,
  limit: 20
})

// 商品类型选择器
const productTypes = ['全部商品', '苹果商品', '普通商品']
const productTypeIndex = ref(0)

// 商品类型变更
const onProductTypeChange = (e: any) => {
  productTypeIndex.value = e.detail.value
  const index = e.detail.value
  
  if (index === 0) {
    // 全部商品 - 需要分别查询
    queryParams.is_apple_product = false
  } else if (index === 1) {
    // 苹果商品
    queryParams.is_apple_product = true
  } else {
    // 普通商品
    queryParams.is_apple_product = false
  }
}

// 加载商品
const loadProducts = async () => {
  if (!queryParams.app_name.trim()) {
    uni.showToast({
      title: '请输入应用名称',
      icon: 'none'
    })
    return
  }

  loading.value = true
  queryParams.skip = 0
  
  try {
    let result
    
    if (productTypeIndex.value === 0) {
      // 全部商品：先查询苹果商品，再查询普通商品
      const [appleResult, normalResult] = await Promise.all([
        productsApi.getAppleProducts(queryParams.app_name, 0, queryParams.limit || 20),
        productsApi.getNonAppleProducts(queryParams.app_name, 0, queryParams.limit || 20)
      ])
      
      products.value = [...(appleResult.data || []), ...(normalResult.data || [])]
    } else {
      result = await productsApi.getAllProducts(queryParams)
      products.value = result.data || []
    }
    
    hasMore.value = (products.value.length === queryParams.limit)
    
    if (products.value.length === 0) {
      uni.showToast({
        title: '未找到相关商品',
        icon: 'none'
      })
    }
  } catch (error) {
    console.error('加载商品失败:', error)
    uni.showToast({
      title: '加载失败，请重试',
      icon: 'none'
    })
  } finally {
    loading.value = false
  }
}

// 加载更多商品
const loadMoreProducts = async () => {
  if (!hasMore.value || loadingMore.value) return
  
  loadingMore.value = true
  const nextSkip = products.value.length
  
  try {
    const newParams = { ...queryParams, skip: nextSkip }
    const result = await productsApi.getAllProducts(newParams)
    
    if (result.data && result.data.length > 0) {
      products.value.push(...result.data)
      hasMore.value = result.data.length === queryParams.limit
    } else {
      hasMore.value = false
    }
  } catch (error) {
    console.error('加载更多失败:', error)
    uni.showToast({
      title: '加载失败，请重试',
      icon: 'none'
    })
  } finally {
    loadingMore.value = false
  }
}

// 商品点击事件
const onProductClick = (product: ProductInfo) => {
  console.log('点击商品:', product)
  // 可以在这里处理商品详情跳转或其他逻辑
  uni.showModal({
    title: '商品信息',
    content: `商品名称：${product.product_name}\n价格：¥${product.price}\n类型：${product.is_apple_product ? '苹果商品' : '普通商品'}`,
    showCancel: false
  })
}

// 页面加载时的默认行为（可选）
onMounted(() => {
  // 如果需要页面加载时自动查询，可以设置默认应用名称
  // queryParams.app_name = 'default_app'
  // loadProducts()
})
</script>

<style scoped>
.products-container {
  padding: 20rpx;
  background-color: #f5f5f5;
  min-height: 100vh;
}

.filter-section {
  background: white;
  padding: 30rpx;
  border-radius: 20rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.1);
}

.filter-item {
  display: flex;
  align-items: center;
  margin-bottom: 20rpx;
}

.filter-label {
  font-weight: bold;
  width: 160rpx;
  color: #333;
}

.filter-input {
  flex: 1;
  padding: 20rpx;
  border: 2rpx solid #ddd;
  border-radius: 10rpx;
  background: #fafafa;
}

.filter-picker {
  flex: 1;
}

.picker-display {
  padding: 20rpx;
  border: 2rpx solid #ddd;
  border-radius: 10rpx;
  background: #fafafa;
}

.search-btn {
  width: 100%;
  background: #007aff;
  color: white;
  border: none;
  border-radius: 10rpx;
  padding: 24rpx;
  font-size: 32rpx;
  margin-top: 10rpx;
}

.products-list {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.empty-state {
  text-align: center;
  padding: 100rpx 0;
  color: #999;
  font-size: 28rpx;
}

.product-item {
  background: white;
  padding: 30rpx;
  border-radius: 20rpx;
  box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.1);
}

.product-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15rpx;
}

.product-name {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
  flex: 1;
}

.product-price {
  font-size: 36rpx;
  font-weight: bold;
  color: #ff6b6b;
}

.product-info {
  margin-bottom: 20rpx;
}

.product-description {
  font-size: 28rpx;
  color: #666;
  line-height: 1.4;
}

.product-tags {
  display: flex;
  gap: 15rpx;
  flex-wrap: wrap;
}

.tag {
  padding: 8rpx 16rpx;
  border-radius: 20rpx;
  font-size: 24rpx;
  background: #f0f0f0;
  color: #666;
}

.apple-tag {
  background: #ff9500;
  color: white;
}

.active-tag {
  background: #34c759;
  color: white;
}

.app-tag {
  background: #007aff;
  color: white;
}

.load-more {
  text-align: center;
  margin-top: 30rpx;
}

.load-more-btn {
  background: #f0f0f0;
  color: #666;
  border: none;
  border-radius: 10rpx;
  padding: 20rpx 40rpx;
  font-size: 28rpx;
}

.load-more-btn[disabled] {
  opacity: 0.5;
}
</style>