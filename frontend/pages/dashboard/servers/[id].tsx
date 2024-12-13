function ServerDetails() {
  // ...
  return (
    <div className="server-costs">
      <h3>هزینه‌های سرور</h3>
      <div className="flex justify-between">
        <div>
          <span className="text-gray-600">هزینه ساعتی:</span>
          <span className="font-bold">{server.hourly_price} تومان</span>
        </div>
        <div>
          <span className="text-gray-600">هزینه ماهانه تقریبی:</span>
          <span className="font-bold">{server.monthly_price} تومان</span>
        </div>
      </div>
      <div className="mt-4">
        <span className="text-gray-600">کارکرد فعلی:</span>
        <span className="font-bold">
          {calculateUsageHours(server.last_charge_at)} ساعت
        </span>
      </div>
    </div>
  );
} 