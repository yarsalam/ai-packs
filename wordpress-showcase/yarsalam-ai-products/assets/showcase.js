(function () {
  "use strict";

  const root = document.querySelector(".yap");
  if (!root) return;

  const titles = {
    overview: "نمای کلی",
    queue: "صف بررسی",
    policies: "سیاست‌ها و قوانین"
  };

  function activateTab(tabName) {
    root.querySelectorAll("[data-yap-tab]").forEach(function (button) {
      const active = button.getAttribute("data-yap-tab") === tabName;
      button.classList.toggle("is-active", active);
      button.setAttribute("aria-pressed", active ? "true" : "false");
    });
    root.querySelectorAll("[data-yap-panel]").forEach(function (panel) {
      panel.hidden = panel.getAttribute("data-yap-panel") !== tabName;
    });
    const title = root.querySelector("[data-yap-current-title]");
    if (title && titles[tabName]) title.textContent = titles[tabName];
  }

  root.addEventListener("click", function (event) {
    const tab = event.target.closest("[data-yap-tab]");
    if (tab && root.contains(tab)) {
      activateTab(tab.getAttribute("data-yap-tab"));
      return;
    }

    const jump = event.target.closest("[data-yap-go]");
    if (jump && root.contains(jump)) {
      activateTab(jump.getAttribute("data-yap-go"));
      return;
    }

    const decision = event.target.closest("[data-yap-decision]");
    if (decision && root.contains(decision)) {
      const card = decision.closest("[data-review-card]");
      if (!card) return;

      const selected = decision.getAttribute("data-yap-decision");
      const messages = {
        allow: "تأیید شد — این تصمیم فقط در پیش‌نمایش ثبت شده است.",
        review: "برای بررسی بیشتر نگه داشته شد — فقط تغییر نمایشی.",
        block: "مسدود شد — این تصمیم به هیچ کاربر واقعی اعمال نشده است."
      };
      const feedback = card.querySelector(".yap-review-feedback");
      if (feedback) feedback.textContent = messages[selected] || "تصمیم نمونه ثبت شد.";

      card.setAttribute("data-demo-status", selected);
      card.querySelectorAll("[data-yap-decision]").forEach(function (button) {
        button.classList.toggle("is-selected", button === decision);
      });

      const key = card.getAttribute("data-review-card");
      const overviewRow = root.querySelector('[data-yap-row="' + key + '"]');
      if (overviewRow) {
        const state = overviewRow.querySelector(".yap-state");
        if (state) {
          state.className = "yap-state " + (
            selected === "allow" ? "yap-state-approved" :
            selected === "block" ? "yap-state-blocked" : "yap-state-review"
          );
          state.textContent = selected === "allow" ? "تأییدشده" :
            selected === "block" ? "مسدودشده" : "در انتظار بررسی";
        }
      }
      return;
    }

    const filter = event.target.closest("[data-yap-filter]");
    if (filter && root.contains(filter)) {
      const filterName = filter.getAttribute("data-yap-filter");
      root.querySelectorAll("[data-yap-filter]").forEach(function (button) {
        button.classList.toggle("is-selected", button === filter);
      });
      root.querySelectorAll("[data-review-card]").forEach(function (card) {
        const visible =
          filterName === "all" ||
          (filterName === "high" && card.getAttribute("data-risk") === "high") ||
          (filterName === "reported" && card.getAttribute("data-reported") === "1") ||
          (filterName === "reviewed" && ["allow", "block"].includes(card.getAttribute("data-demo-status")));
        card.hidden = !visible;
      });
    }

    const policySave = event.target.closest("[data-yap-policy-save]");
    if (policySave && root.contains(policySave)) {
      const note = root.querySelector(".yap-policy-feedback");
      if (note) note.textContent = "پیش‌نمایش تنظیمات تغییر کرد؛ برای این نسخه هیچ داده‌ای ذخیره یا به سرور ارسال نشد.";
    }
  });

  const slider = root.querySelector("[data-yap-threshold]");
  const sliderOutput = root.querySelector("[data-yap-threshold-value]");
  if (slider && sliderOutput) {
    slider.addEventListener("input", function () {
      const value = (Number(slider.value) / 100).toFixed(2);
      sliderOutput.textContent = value.replace(/[0-9]/g, function (digit) {
        return "۰۱۲۳۴۵۶۷۸۹"[Number(digit)];
      });
    });
  }

  root.querySelectorAll("[data-yap-policy]").forEach(function (select) {
    select.addEventListener("change", function () {
      select.classList.add("is-modified");
    });
  });

  activateTab("overview");
}());
