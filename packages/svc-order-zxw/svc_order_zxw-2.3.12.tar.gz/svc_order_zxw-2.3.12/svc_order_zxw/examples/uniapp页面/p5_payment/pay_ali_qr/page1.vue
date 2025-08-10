<template>
	<view class="container">
		<view class="header">
			<text class="title">支付详情</text>
		</view>
		<view class="content">
			<text class="price">支付金额: ¥{{ paymentPrice }}</text>
			<text class="quantity">购买数量: {{ quantity }}</text>
			<button class="pay-button" @click="handlePayment">发起支付</button>
		</view>
	</view>
</template>

<script setup>
import { ref } from 'vue';
import { onLoad, onShow } from "@dcloudio/uni-app";
import { orderApi } from './api_app_url.ts';

const paymentPrice = ref(0.01);
const productId = ref(1);
const quantity = ref(1);

const loadUrlParams = (options) => {
	paymentPrice.value = parseFloat(options.paymentPrice || 0.0);
	productId.value = parseInt(options.productId || -1);
	quantity.value = parseInt(options.quantity || 1);

	console.log("paymentPrice:", paymentPrice.value);
	console.log("productId:", productId.value);
	console.log("quantity:", quantity.value);
};
onLoad((options) => {
	loadUrlParams(options);
});

const handlePayment = async () => {
	try {
		uni.showLoading({
			title: '支付中...',
			mask: true
		});

		// 创建订单
		const orderResponse = await orderApi.createAlipayOrder({
			product_id: productId.value,
			payment_price: paymentPrice.value,
			quantity: quantity.value
		});
		console.log("orderResponse:", orderResponse);

		// 发起支付
		const paymentResponse = await orderApi.initiateAlipayPayment({
			order_number: orderResponse.order_number
		});
		console.log("paymentResponse:", paymentResponse);

		// 跳转到页面二并传递支付信息
		console.log("跳转页面...");
		uni.navigateTo({
			url: `/pages/p5_payment/pay_ali_qr/page2?payment_price=${encodeURIComponent(paymentPrice.value)}&qr_uri=${encodeURIComponent(paymentResponse.qr_uri)}&order_number=${encodeURIComponent(paymentResponse.order_number)}`
		});
	} catch (error) {
		console.error('支付过程出错', error);
	} finally {
		uni.hideLoading();
	}
};
</script>

<style lang="scss">
@import '@/uni.scss';

.container {
	display: flex;
	flex-direction: column;
	justify-content: space-between;
	align-items: center;
	height: 100vh;
	background-color: $uni-bg-color-grey;
	padding: $uni-spacing-row-lg;
}

.header {
	width: 100%;
	padding: $uni-spacing-col-lg 0;
	background-color: $uni-color-primary;
	text-align: center;
	box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
	border-radius: $uni-border-radius-lg;
}

.title {
	color: $uni-text-color-inverse;
	font-size: $uni-font-size-lg;
	font-weight: bold;
}

.content {
	flex: 1;
	display: flex;
	flex-direction: column;
	justify-content: center;
	align-items: center;
	width: 100%;
	background-color: $uni-bg-color;
	padding: $uni-spacing-col-lg;
	box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
	border-radius: $uni-border-radius-lg;
	margin-top: $uni-spacing-row-lg;
}

.price {
	font-size: $uni-font-size-title;
	margin-bottom: $uni-spacing-row-lg;
	color: $uni-text-color;
	font-weight: bold;
}

.quantity {
	font-size: $uni-font-size-base;
	margin-bottom: $uni-spacing-row-base;
	color: $uni-text-color;
}

.pay-button {
	padding: $uni-spacing-col-base $uni-spacing-row-lg;
	background-color: $uni-color-primary;
	color: $uni-text-color-inverse;
	border-radius: $uni-border-radius-lg;
	font-size: $uni-font-size-lg;
	box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
	transition: all 0.3s ease;

	&:active {
		background-color: darken($uni-color-primary, 10%);
		transform: scale(0.98);
	}
}
</style>