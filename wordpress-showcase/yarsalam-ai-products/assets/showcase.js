(function () {
  "use strict";
  const samples = {
    contact: {
      message: "بیا ادامه صحبت رو بیرون از اپ در واتساپ انجام بدیم.",
      action: "نیازمند بررسی انسانی",
      reason: "دلیل نمونه: تلاش برای انتقال گفتگو به خارج از پلتفرم."
    },
    clean: {
      message: "سلام، روز خوبی داشته باشی. از آشنایی باهات خوشحالم.",
      action: "مجاز",
      reason: "دلیل نمونه: سیگنال تخلفی در این سناریوی نمایشی وجود ندارد."
    },
    custom: {
      message: "این عبارت در سیاست اختصاصی کسب‌وکار تعریف شده است.",
      action: "مسدود شود",
      reason: "دلیل نمونه: عبارت در فهرست سفارشی مسدودسازی مدیر سایت قرار دارد."
    }
  };
  document.querySelectorAll(".yap-demo").forEach(function (demo) {
    const message = demo.querySelector("#yap-demo-message");
    const action = demo.querySelector("#yap-demo-action");
    const reason = demo.querySelector("#yap-demo-reason");
    demo.querySelectorAll("[data-sample]").forEach(function (button) {
      button.addEventListener("click", function () {
        const sample = samples[button.getAttribute("data-sample")];
        if (!sample) return;
        message.textContent = sample.message;
        action.textContent = sample.action;
        reason.textContent = sample.reason;
        demo.querySelectorAll("[data-sample]").forEach(function (item) {
          item.classList.toggle("is-active", item === button);
        });
      });
    });
  });
}());
