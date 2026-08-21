
(() => {
  "use strict";

  const dadosTag = document.getElementById("dados-graficos");
  const dadosGraficos = dadosTag ? JSON.parse(dadosTag.textContent || "{}") : {};
  const dadosFunil = dadosGraficos.funil || {};
  const dadosReceita = dadosGraficos.receita || {};

  const normalize = (value = "") =>
    value.toString().normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().trim();

  /* Dialogs */
  document.querySelectorAll("[data-open-dialog]").forEach((button) => {
    button.addEventListener("click", () => {
      const dialog = document.getElementById(button.dataset.openDialog);
      if (dialog && typeof dialog.showModal === "function") dialog.showModal();
    });
  });

  document.querySelectorAll("[data-close-dialog]").forEach((button) => {
    button.addEventListener("click", () => {
      const dialog = button.closest("dialog");
      if (dialog) dialog.close();
    });
  });

  document.querySelectorAll("dialog").forEach((dialog) => {
    dialog.addEventListener("click", (event) => {
      if (event.target === dialog) dialog.close();
    });
  });

  /* Atalhos: / busca global | n novo contato */
  document.addEventListener("keydown", (event) => {
    const target = event.target;
    const isTyping = target instanceof HTMLInputElement ||
                     target instanceof HTMLTextAreaElement ||
                     target instanceof HTMLSelectElement ||
                     target?.isContentEditable;

    if (!isTyping && event.key === "/") {
      event.preventDefault();
      document.getElementById("busca-geral")?.focus();
    }

    if (!isTyping && event.key.toLowerCase() === "n") {
      const dialog = document.getElementById("modal-novo-contato");
      if (dialog && !dialog.open) dialog.showModal();
    }
  });

  /* Filtro local de contatos */
  const contactSearch = document.getElementById("filtro-contatos");
  const stageFilter = document.getElementById("filtro-etapa");
  const contactRows = [...document.querySelectorAll("[data-contact-row]")];
  const contactCount = document.getElementById("contacts-count");

  function filterContacts(){
    const query = normalize(contactSearch?.value);
    const stage = normalize(stageFilter?.value);
    let visible = 0;

    contactRows.forEach((row) => {
      const matchesText = !query || normalize(row.innerText).includes(query);
      const matchesStage = !stage || normalize(row.dataset.stage) === stage;
      const show = matchesText && matchesStage;
      row.hidden = !show;
      if (show) visible += 1;
    });

    if (contactCount) {
      contactCount.textContent = (query || stage)
        ? `${visible} de ${contactRows.length}`
        : `${contactRows.length} no total`;
    }
  }

  contactSearch?.addEventListener("input", filterContacts);
  stageFilter?.addEventListener("change", filterContacts);

  /* Filtro local de tarefas */
  const taskButtons = [...document.querySelectorAll("[data-task-filter]")];
  const taskItems = [...document.querySelectorAll(".task-item[data-status]")];
  const taskCount = document.getElementById("task-count");

  taskButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const filter = button.dataset.taskFilter;

      taskButtons.forEach((item) => {
        const active = item === button;
        item.classList.toggle("is-active", active);
        item.setAttribute("aria-pressed", active ? "true" : "false");
      });

      let visible = 0;
      taskItems.forEach((item) => {
        const show = filter === "all" || item.dataset.status === filter;
        item.hidden = !show;
        if (show) visible += 1;
      });

      if (taskCount) {
        const label = filter === "all" ? "itens" :
                      filter === "done" ? "concluídas" :
                      filter === "overdue" ? "atrasadas" : "pendentes";
        taskCount.textContent = `${visible} ${label}`;
      }
    });
  });

  /* Navegação contextual */
  const navLinks = [...document.querySelectorAll(".section-nav a")];
  const observedSections = navLinks
    .map((link) => document.querySelector(link.getAttribute("href")))
    .filter(Boolean);

  if ("IntersectionObserver" in window) {
    const observer = new IntersectionObserver((entries) => {
      const visible = entries
        .filter((entry) => entry.isIntersecting)
        .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];

      if (!visible) return;
      navLinks.forEach((link) => {
        const active = link.getAttribute("href") === `#${visible.target.id}`;
        if (active) link.setAttribute("aria-current", "location");
        else link.removeAttribute("aria-current");
      });
    }, { rootMargin: "-25% 0px -60% 0px", threshold: [0.01, .2, .5] });

    observedSections.forEach((section) => observer.observe(section));
  }

  /* Gráficos: cores ligadas aos tokens CSS e atualizadas com o tema do sistema */
  if (typeof Chart !== "undefined") {
    Chart.defaults.font.family = "'IBM Plex Sans', sans-serif";

    const money = new Intl.NumberFormat("pt-BR", {
      style: "currency",
      currency: "BRL",
      maximumFractionDigits: 0
    });

    const cssColor = (name) =>
      getComputedStyle(document.documentElement).getPropertyValue(name).trim();

    const funnelCanvas = document.getElementById("grafico-funil");
    const funnelEmpty = document.getElementById("grafico-funil-vazio");
    const revenueCanvas = document.getElementById("grafico-receita");
    const revenueEmpty = document.getElementById("grafico-receita-vazio");

    const funnelHasData = Array.isArray(dadosFunil?.valores) && dadosFunil.valores.some((v) => Number(v) > 0);
    const revenueHasData = Array.isArray(dadosReceita?.valores) && dadosReceita.valores.some((v) => Number(v) !== 0);

    let funnelChart = null;
    let revenueChart = null;

    function chartPalette(){
      return {
        text: cssColor("--chart-text"),
        grid: cssColor("--chart-grid"),
        blue: cssColor("--chart-blue"),
        green: cssColor("--chart-green"),
        greenFill: cssColor("--chart-green-fill"),
        tooltipBg: cssColor("--chart-tooltip-bg"),
        tooltipText: cssColor("--chart-tooltip-text")
      };
    }

    function makeScales(palette){
      return {
        x: {
          grid: { display: false },
          border: { color: palette.grid },
          ticks: { color: palette.text, font: { size: 10 } }
        },
        y: {
          beginAtZero: true,
          grid: { color: palette.grid },
          border: { display: false },
          ticks: { color: palette.text, font: { size: 10 }, precision: 0 }
        }
      };
    }

    function tooltipTheme(palette){
      return {
        backgroundColor: palette.tooltipBg,
        titleColor: palette.tooltipText,
        bodyColor: palette.tooltipText,
        borderColor: palette.grid,
        borderWidth: 1,
        displayColors: false
      };
    }

    function buildCharts(){
      const palette = chartPalette();
      Chart.defaults.color = palette.text;
      const scales = makeScales(palette);

      if (funnelCanvas && funnelHasData) {
        funnelChart = new Chart(funnelCanvas, {
          type: "bar",
          data: {
            labels: dadosFunil.labels,
            datasets: [{
              label: "Negócios",
              data: dadosFunil.valores,
              backgroundColor: palette.blue,
              borderRadius: 6,
              maxBarThickness: 38
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: { display: false },
              tooltip: {
                ...tooltipTheme(palette),
                callbacks: {
                  label: (context) => `${context.raw} negócio${Number(context.raw) === 1 ? "" : "s"}`
                }
              }
            },
            scales
          }
        });
      } else if (funnelCanvas && funnelEmpty) {
        funnelCanvas.hidden = true;
        funnelEmpty.hidden = false;
      }

      if (revenueCanvas && revenueHasData) {
        revenueChart = new Chart(revenueCanvas, {
          type: "line",
          data: {
            labels: dadosReceita.labels,
            datasets: [{
              label: "Receita",
              data: dadosReceita.valores,
              borderColor: palette.green,
              backgroundColor: palette.greenFill,
              fill: true,
              tension: .32,
              pointRadius: 2.5,
              pointHoverRadius: 5,
              borderWidth: 2
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { intersect: false, mode: "index" },
            plugins: {
              legend: { display: false },
              tooltip: {
                ...tooltipTheme(palette),
                callbacks: {
                  label: (context) => money.format(Number(context.raw || 0))
                }
              }
            },
            scales: {
              x: scales.x,
              y: {
                ...scales.y,
                ticks: {
                  ...scales.y.ticks,
                  callback: (value) => money.format(Number(value))
                }
              }
            }
          }
        });
      } else if (revenueCanvas && revenueEmpty) {
        revenueCanvas.hidden = true;
        revenueEmpty.hidden = false;
      }
    }

    function refreshChartTheme(){
      const palette = chartPalette();
      Chart.defaults.color = palette.text;

      if (funnelChart) {
        funnelChart.data.datasets[0].backgroundColor = palette.blue;
        funnelChart.options.scales = makeScales(palette);
        Object.assign(funnelChart.options.plugins.tooltip, tooltipTheme(palette));
        funnelChart.update("none");
      }

      if (revenueChart) {
        const scales = makeScales(palette);
        revenueChart.data.datasets[0].borderColor = palette.green;
        revenueChart.data.datasets[0].backgroundColor = palette.greenFill;
        revenueChart.options.scales.x = scales.x;
        revenueChart.options.scales.y.grid.color = palette.grid;
        revenueChart.options.scales.y.ticks.color = palette.text;
        Object.assign(revenueChart.options.plugins.tooltip, tooltipTheme(palette));
        revenueChart.update("none");
      }
    }

    buildCharts();

    const themeQuery = window.matchMedia?.("(prefers-color-scheme: dark)");
    if (themeQuery) {
      if (typeof themeQuery.addEventListener === "function") {
        themeQuery.addEventListener("change", refreshChartTheme);
      } else if (typeof themeQuery.addListener === "function") {
        themeQuery.addListener(refreshChartTheme);
      }
    }
  }
})();
