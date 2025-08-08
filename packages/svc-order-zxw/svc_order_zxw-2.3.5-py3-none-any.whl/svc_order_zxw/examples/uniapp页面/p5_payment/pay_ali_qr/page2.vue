<template>
	<view class="container">
		<view class="payment-card">
			<text class="payment-title">支付金额</text>
			<text class="payment-price">¥{{ payment_price }}</text>
			<view class="qr-code-container">
				<image v-if="qr_img" :src="qr_img" class="qr-code-image"></image>
			</view>
			<view v-if="isMobile" class="mobile-pay-link">
				<a :href="qr_uri" target="_blank" class="app-pay-button">去APP支付</a>
			</view>
			<text class="payment-tip">{{ isMobile ? '点击按钮跳转支付宝支付' : '请使用支付宝扫码支付' }}</text>
		</view>
		<button class="status-button" @click="checkStatus">确认已支付</button>
	</view>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { onLoad } from '@dcloudio/uni-app';
import { orderApi } from '@/pages/p5_payment/pay_ali_qr/api_app_url';
import QRCode from 'qrcode'; // 使用新的库

const payment_price = ref(0);
const qr_uri = ref('');
const order_number = ref('');
const qr_img = ref('');
const qrCodeContainer = ref(null);
const isMobile = ref(false);

onLoad((options) => {
	payment_price.value = options.payment_price;
	qr_uri.value = decodeURIComponent(options.qr_uri);
	order_number.value = options.order_number;

	// 检测是否为移动端浏览器
	const userAgent = navigator.userAgent.toLowerCase();
	isMobile.value = /mobile|android|iphone|ipad|phone/i.test(userAgent);
});

onMounted(() => {
	generateQRCode();
});

const generateQRCode = async () => {
	try {
		const qrCodeDataUrl = await QRCode.toDataURL(qr_uri.value, {
			width: 250,
			margin: 1,
			color: {
				dark: '#000000',
				light: '#ffffff'
			}
		});
		qr_img.value = qrCodeDataUrl;
	} catch (error) {
		console.error('生成二维码时发生错误:', error);
		uni.showToast({
			title: '二维码生成失败',
			icon: 'none'
		});
	}
};

const checkStatus = async () => {
	try {
		const paymentResponse = await orderApi.queryAlipayPaymentStatus({
			order_number: order_number.value
		});
		if (paymentResponse.payment_status === 'paid') {
			uni.showToast({
				title: '支付成功',
				icon: 'success'
			});
			uni.navigateTo({
				url: '/pages/p6_personal-center/p1-index'
			});
		} else {
			uni.showToast({
				title: '支付未完成',
				icon: 'none'
			});
		}
	} catch (error) {
		console.error('查询支付状态出错', error);
		uni.showToast({
			title: '查询支付状态失败',
			icon: 'none'
		});
	}
};
</script>

<style lang="scss">
@import '@/uni.scss';

.container {
	display: flex;
	flex-direction: column;
	justify-content: center;
	align-items: center;
	min-height: 100vh;
	background-color: $uni-bg-color-grey;
	padding: 20px;
	box-sizing: border-box;
}

.payment-card {
	background-color: $uni-bg-color;
	border-radius: $uni-border-radius-lg;
	padding: 30px;
	box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
	display: flex;
	flex-direction: column;
	align-items: center;
	width: 90%;
	max-width: 400px;
}

.payment-title {
	font-size: $uni-font-size-lg;
	color: $uni-text-color-grey;
	margin-bottom: 10px;
}

.payment-price {
	font-size: 36px;
	font-weight: bold;
	color: $uni-text-color;
	margin-bottom: 25px;
}

.qr-code-container {
	width: 220px;
	height: 220px;
	display: flex;
	justify-content: center;
	align-items: center;
	background-color: $uni-bg-color;
	border-radius: $uni-border-radius-sm;
	box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
	margin-bottom: 25px;
}

.payment-tip {
	font-size: $uni-font-size-base;
	color: $uni-text-color-grey;
	margin-bottom: 20px;
}

.status-button {
	margin-top: 30px;
	padding: 12px 24px;
	background-color: $uni-color-primary;
	color: $uni-text-color-inverse;
	font-size: $uni-font-size-lg;
	border: none;
	border-radius: $uni-border-radius-lg;
	box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
	transition: all 0.3s ease;

	&:active {
		transform: translateY(2px);
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.15);
	}
}

.qr-code-image {
	width: 220px;
	height: 220px;
}

.mobile-pay-link {
	margin: 20px 0;
}

.app-pay-button {
	display: inline-block;
	padding: 12px 30px;
	background-color: #1677ff; // 支付宝蓝色
	color: #ffffff;
	text-decoration: none;
	border-radius: $uni-border-radius-lg;
	font-size: $uni-font-size-lg;
	transition: all 0.3s ease;

	&:active {
		opacity: 0.8;
	}
}
</style>