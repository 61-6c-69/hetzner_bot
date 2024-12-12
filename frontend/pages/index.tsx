import Head from 'next/head';
import Link from 'next/link';
import Image from 'next/image';

export async function getStaticProps() {
  // دریافت قیمت‌ها از API
  const res = await fetch(`${process.env.API_URL}/prices`);
  const prices = await res.json();

  return {
    props: {
      prices
    },
    // هر 24 ساعت صفحه رو دوباره بساز
    revalidate: 60 * 60 * 24
  };
}

export default function Home({ prices }) {
  return (
    <>
      <Head>
        <title>خرید سرور ارزان هتزنر | سرور مجازی آلمان با قیمت مناسب</title>
        <meta name="description" content="خرید سرور مجازی ارزان در آلمان با بهترین قیمت و کیفیت. پشتیبانی 24/7، تحویل آنی، پنل مدیریت فارسی و امکان پرداخت با تومان." />
        <meta name="keywords" content="سرور مجازی آلمان, خرید سرور ارزان, هتزنر, سرور vps" />
        <meta property="og:title" content="خرید سرور ارزان هتزنر | سرور مجازی آلمان" />
        <meta property="og:description" content="خرید سرور مجازی ارزان در آلمان با بهترین قیمت و کیفیت. پشتیبانی 24/7، تحویل آنی." />
        <link rel="canonical" href="https://yourdomain.com" />
      </Head>

      <div className="bg-white">
        {/* Hero Section */}
        <div className="relative bg-gradient-to-r from-blue-600 to-blue-800">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
            <div className="text-center">
              <h1 className="text-4xl tracking-tight font-extrabold text-white sm:text-5xl md:text-6xl">
                <span className="block">سرور مجازی آلمان</span>
                <span className="block text-blue-200">با بهترین قیمت و کیفیت</span>
              </h1>
              <p className="mt-3 max-w-md mx-auto text-base text-blue-100 sm:text-lg md:mt-5 md:text-xl md:max-w-3xl">
                خرید سرور مجازی با قیمت استثنایی در دیتاسنترهای معتبر آلمان. پرداخت به تومان، تحویل آنی و پشتیبانی 24 ساعته.
              </p>
              <div className="mt-5 max-w-md mx-auto sm:flex sm:justify-center md:mt-8">
                <div className="rounded-md shadow">
                  <Link href="/auth/login">
                    <a className="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-blue-700 bg-white hover:bg-blue-50 md:py-4 md:text-lg md:px-10">
                      شروع رایگان
                    </a>
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Features */}
        <div className="py-16 bg-gray-50 overflow-hidden lg:py-24">
          <div className="relative max-w-xl mx-auto px-4 sm:px-6 lg:px-8 lg:max-w-7xl">
            <div className="relative">
              <h2 className="text-center text-3xl leading-8 font-extrabold tracking-tight text-gray-900 sm:text-4xl">
                چرا سرور مجازی ما؟
              </h2>
              <p className="mt-4 max-w-3xl mx-auto text-center text-xl text-gray-500">
                با بیش از 5 سال سابقه در ارائه خدمات سرور مجازی، بهترین کیفیت را با مناسب‌ترین قیمت ارائه می‌دهیم
              </p>
            </div>

            <div className="relative mt-12 lg:mt-24 lg:grid lg:grid-cols-2 lg:gap-8 lg:items-center">
              <div className="relative">
                <h3 className="text-2xl font-extrabold text-gray-900 tracking-tight sm:text-3xl">
                  مزایای سرور مجازی آلمان
                </h3>
                <p className="mt-3 text-lg text-gray-500">
                  سرورهای مجازی ما در بهترین دیتاسنترهای آلمان میزبانی می‌شوند و از نظر کیفیت و پایداری در بالاترین سطح قرار دارند.
                </p>

                <dl className="mt-10 space-y-10">
                  <div className="relative">
                    <dt>
                      <div className="absolute flex items-center justify-center h-12 w-12 rounded-md bg-blue-500 text-white">
                        {/* Icon */}
                      </div>
                      <p className="mr-16 text-lg leading-6 font-medium text-gray-900">پینگ عالی</p>
                    </dt>
                    <dd className="mt-2 mr-16 text-base text-gray-500">
                      پینگ بسیار مناسب برای ایران و خاورمیانه
                    </dd>
                  </div>

                  <div className="relative">
                    <dt>
                      <div className="absolute flex items-center justify-center h-12 w-12 rounded-md bg-blue-500 text-white">
                        {/* Icon */}
                      </div>
                      <p className="mr-16 text-lg leading-6 font-medium text-gray-900">قیمت استثنایی</p>
                    </dt>
                    <dd className="mt-2 mr-16 text-base text-gray-500">
                      ارزان‌ترین قیمت سرور مجازی در ایران با کیفیت اروپایی
                    </dd>
                  </div>

                  <div className="relative">
                    <dt>
                      <div className="absolute flex items-center justify-center h-12 w-12 rounded-md bg-blue-500 text-white">
                        {/* Icon */}
                      </div>
                      <p className="mr-16 text-lg leading-6 font-medium text-gray-900">پشتیبانی 24/7</p>
                    </dt>
                    <dd className="mt-2 mr-16 text-base text-gray-500">
                      پشتیبانی شبانه‌روزی از طریق تیکت و تلگرام
                    </dd>
                  </div>
                </dl>
              </div>

              <div className="mt-10 -mx-4 relative lg:mt-0">
                <Image 
                  src="/images/server-rack.jpg"
                  alt="دیتاسنتر هتزنر در آلمان"
                  width={500}
                  height={300}
                  className="rounded-lg shadow-lg"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Pricing */}
        <div className="bg-white py-16 sm:py-24">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center">
              <h2 className="text-3xl font-extrabold text-gray-900 sm:text-4xl">
                تعرفه‌های سرور مجازی
              </h2>
              <p className="mt-4 text-lg text-gray-600">
                پرداخت به صو��ت ساعتی، بدون هزینه اضافی
              </p>
            </div>

            <div className="mt-16 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {/* Basic Plan */}
              <div className="border border-gray-200 rounded-lg shadow-sm p-6 bg-white hover:border-blue-500 transition-colors duration-300">
                <h3 className="text-lg font-medium text-gray-900">{prices.basic.name}</h3>
                <p className="mt-4 text-sm text-gray-500">مناسب برای شروع کار</p>
                <div className="pricing-card mt-8">
                  <div className="prices space-y-4">
                    <div className="daily">
                      <span className="text-4xl font-extrabold text-gray-900">
                        {prices.basic.daily.toLocaleString()}
                      </span>
                      <span className="text-base font-medium text-gray-500"> تومان / روز</span>
                      <p className="text-sm text-gray-500 mt-1">
                        ({prices.basic.hourly.toLocaleString()} تومان در ساعت)
                      </p>
                    </div>
                  </div>
                  <ul className="mt-6 space-y-4">
                    <li className="flex items-center">
                      <span className="text-blue-500 mr-2">✓</span>
                      <span>{prices.basic.resources.ram}GB RAM</span>
                    </li>
                    <li className="flex items-center">
                      <span className="text-blue-500 mr-2">✓</span>
                      <span>{prices.basic.resources.cpu} Core CPU</span>
                    </li>
                    <li className="flex items-center">
                      <span className="text-blue-500 mr-2">✓</span>
                      <span>{prices.basic.resources.disk}GB SSD</span>
                    </li>
                    <li className="flex items-center">
                      <span className="text-blue-500 mr-2">✓</span>
                      <span>ترافیک نامحدود</span>
                    </li>
                  </ul>
                  <Link href="/auth/login">
                    <a className="mt-8 block w-full bg-blue-600 text-white text-center py-2 rounded-md hover:bg-blue-700">
                      سفارش
                    </a>
                  </Link>
                </div>
              </div>

              {/* Pro Plan */}
              <div className="border border-blue-500 rounded-lg shadow-sm p-6 bg-white relative">
                <div className="absolute top-0 right-0 mt-2 mr-2">
                  <span className="bg-blue-500 text-white px-2 py-1 rounded-full text-xs">پرفروش</span>
                </div>
                <h3 className="text-lg font-medium text-gray-900">پلن حرفه‌ای</h3>
                <p className="mt-4 text-sm text-gray-500">مناسب برای کسب و کارهای متوسط</p>
                <div className="pricing-card mt-8">
                  <div className="prices space-y-4">
                    <div className="daily">
                      <span className="text-4xl font-extrabold text-gray-900">14,400</span>
                      <span className="text-base font-medium text-gray-500"> تومان / روز</span>
                      <p className="text-sm text-gray-500 mt-1">(600 تومان در ساعت)</p>
                    </div>
                  </div>
                  <ul className="mt-6 space-y-4">
                    <li className="flex items-center">
                      <span className="text-blue-500 mr-2">✓</span>
                      <span>4GB RAM</span>
                    </li>
                    <li className="flex items-center">
                      <span className="text-blue-500 mr-2">✓</span>
                      <span>2 Core CPU</span>
                    </li>
                    <li className="flex items-center">
                      <span className="text-blue-500 mr-2">✓</span>
                      <span>40GB SSD</span>
                    </li>
                    <li className="flex items-center">
                      <span className="text-blue-500 mr-2">✓</span>
                      <span>ترافیک نامحدود</span>
                    </li>
                    <li className="flex items-center">
                      <span className="text-blue-500 mr-2">✓</span>
                      <span>پشتیبانی اولویت‌دار</span>
                    </li>
                  </ul>
                  <Link href="/auth/login">
                    <a className="mt-8 block w-full bg-blue-600 text-white text-center py-2 rounded-md hover:bg-blue-700">
                      سفارش
                    </a>
                  </Link>
                </div>
              </div>

              {/* Enterprise Plan */}
              <div className="border border-gray-200 rounded-lg shadow-sm p-6 bg-white hover:border-blue-500 transition-colors duration-300">
                <h3 className="text-lg font-medium text-gray-900">پلن سازمانی</h3>
                <p className="mt-4 text-sm text-gray-500">مناسب برای کسب و کارهای بزرگ</p>
                <div className="pricing-card mt-8">
                  <div className="prices space-y-4">
                    <div className="daily">
                      <span className="text-4xl font-extrabold text-gray-900">24,000</span>
                      <span className="text-base font-medium text-gray-500"> تومان / روز</span>
                      <p className="text-sm text-gray-500 mt-1">(1,000 تومان در ساعت)</p>
                    </div>
                  </div>
                  <ul className="mt-6 space-y-4">
                    <li className="flex items-center">
                      <span className="text-blue-500 mr-2">✓</span>
                      <span>8GB RAM</span>
                    </li>
                    <li className="flex items-center">
                      <span className="text-blue-500 mr-2">✓</span>
                      <span>4 Core CPU</span>
                    </li>
                    <li className="flex items-center">
                      <span className="text-blue-500 mr-2">✓</span>
                      <span>80GB SSD</span>
                    </li>
                    <li className="flex items-center">
                      <span className="text-blue-500 mr-2">✓</span>
                      <span>ترافیک نامحدود</span>
                    </li>
                    <li className="flex items-center">
                      <span className="text-blue-500 mr-2">✓</span>
                      <span>پشتیبانی اختصاصی</span>
                    </li>
                  </ul>
                  <Link href="/auth/login">
                    <a className="mt-8 block w-full bg-blue-600 text-white text-center py-2 rounded-md hover:bg-blue-700">
                      سفارش
                    </a>
                  </Link>
                </div>
              </div>
            </div>

            {/* Additional Info */}
            <div className="mt-12 text-center">
              <p className="text-gray-600">
                💡 هزینه‌ها به صورت ساعتی محاسبه می‌شود و فقط برای زمان روشن بودن سرور از شما کسر می‌شود.
              </p>
              <p className="text-gray-600 mt-2">
                💰 برای شروع کار، فقط نیاز به شارژ حساب به اندازه هزینه یک روز دارید.
              </p>
            </div>
          </div>
        </div>

        {/* FAQ */}
        <div className="bg-gray-50 py-16">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <h2 className="text-3xl font-extrabold text-gray-900 text-center mb-8">
              سوالات متداول
            </h2>
            <div className="max-w-3xl mx-auto divide-y-2 divide-gray-200">
              <dl className="space-y-6 divide-y divide-gray-200">
                <div className="pt-6">
                  <dt className="text-lg">
                    <button className="text-right w-full flex justify-between items-start text-gray-400">
                      <span className="font-medium text-gray-900">
                        چرا سرور مجازی آلمان؟
                      </span>
                    </button>
                  </dt>
                  <dd className="mt-2 pr-12">
                    <p className="text-base text-gray-500">
                      سرورهای آلمان به دلیل موقعیت جغرافیایی مناسب، پینگ عالی برای ایران و کیفیت بالای زیرساخت‌ها، بهترین گزینه برای کاربران ایرانی هستند.
                    </p>
                  </dd>
                </div>

                <div className="pt-6">
                  <dt className="text-lg">
                    <button className="text-right w-full flex justify-between items-start text-gray-400">
                      <span className="font-medium text-gray-900">
                        نحوه پرداخت چگونه است؟
                      </span>
                    </button>
                  </dt>
                  <dd className="mt-2 pr-12">
                    <p className="text-base text-gray-500">
                      پرداخت به صورت ریالی و از طریق درگاه‌های بانکی داخلی انجام می‌شود. امکان پرداخت دوره‌ای ماهانه نیز وجود دارد.
                    </p>
                  </dd>
                </div>
              </dl>
            </div>
          </div>
        </div>

        {/* CTA */}
        <div className="bg-blue-700">
          <div className="max-w-2xl mx-auto text-center py-16 px-4 sm:py-20 sm:px-6 lg:px-8">
            <h2 className="text-3xl font-extrabold text-white sm:text-4xl">
              <span className="block">آماده شروع هستید؟</span>
              <span className="block text-blue-200">همین حالا سرور خود را راه‌اندازی کنید</span>
            </h2>
            <p className="mt-4 text-lg leading-6 text-blue-200">
              تنها در چند دقیقه صاحب یک سرور مجازی قدرتمند در آلمان شوید
            </p>
            <Link href="/auth/login">
              <a className="mt-8 w-full inline-flex items-center justify-center px-5 py-3 border border-transparent text-base font-medium rounded-md text-blue-700 bg-white hover:bg-blue-50 sm:w-auto">
                شروع رایگان
              </a>
            </Link>
          </div>
        </div>
      </div>
    </>
  );
}