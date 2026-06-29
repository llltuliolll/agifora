/* ============================================================
   AGIFORA — JavaScript principal
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {
  initTaxasExtras();
  initCurrencyMask();
  initTooltips();
  initCalculadoraPreview();
  initNavActiveState();
});

/* ---- Máscara de moeda ---- */
function initCurrencyMask() {
  document.querySelectorAll('input[data-mask="currency"]').forEach(input => {
    input.addEventListener('input', e => {
      let val = e.target.value.replace(/\D/g, '');
      val = (parseInt(val, 10) / 100).toFixed(2);
      e.target.value = val === 'NaN' ? '' : val;
    });
  });
}

/* ---- Gerenciar taxas extras dinamicamente ---- */
function initTaxasExtras() {
  const container = document.getElementById('taxas-container');
  const addBtn = document.getElementById('add-taxa-btn');
  const jsonInput = document.getElementById('taxas_json');

  if (!container || !addBtn) return;

  let taxas = [];

  function render() {
    container.innerHTML = '';
    if (taxas.length === 0) {
      container.innerHTML = '<p class="text-muted-sm">Nenhum encargo extra adicionado.</p>';
    }
    taxas.forEach((t, i) => {
      const div = document.createElement('div');
      div.className = 'taxa-item';
      div.innerHTML = `
        <span class="taxa-nome">${t.nome_taxa}</span>
        <span class="taxa-valor">R$ ${parseFloat(t.valor).toFixed(2)}</span>
        <button type="button" class="btn btn-sm btn-link text-danger p-0 ms-2" onclick="removeTaxa(${i})">
          <i data-feather="x" style="width:16px;height:16px"></i>
        </button>`;
      container.appendChild(div);
    });
    feather.replace();
    if (jsonInput) jsonInput.value = JSON.stringify(taxas);
    updatePreview();
  }

  window.removeTaxa = (idx) => {
    taxas.splice(idx, 1);
    render();
  };

  addBtn.addEventListener('click', () => {
    const nomeEl = document.getElementById('taxa-nome-input');
    const valorEl = document.getElementById('taxa-valor-input');
    const nome = nomeEl?.value.trim();
    const valor = parseFloat(valorEl?.value);

    if (!nome) { showAlert('Digite o nome do encargo.', 'warning'); return; }
    if (isNaN(valor) || valor < 0) { showAlert('Digite um valor válido.', 'warning'); return; }

    taxas.push({ nome_taxa: nome, valor: valor.toFixed(2) });
    nomeEl.value = '';
    valorEl.value = '';
    render();
  });

  render();
}

/* ---- Preview em tempo real do cálculo ---- */
function initCalculadoraPreview() {
  const fields = ['id_valor_a_vista', 'id_num_parcelas', 'id_valor_parcela'];
  fields.forEach(id => {
    const el = document.getElementById(id);
    if (el) el.addEventListener('input', updatePreview);
  });
  updatePreview();
}

function updatePreview() {
  const vistaEl = document.getElementById('id_valor_a_vista');
  const numEl = document.getElementById('id_num_parcelas');
  const parcEl = document.getElementById('id_valor_parcela');
  const previewEl = document.getElementById('calc-preview');

  if (!vistaEl || !numEl || !parcEl || !previewEl) return;

  const vista = parseFloat(vistaEl.value) || 0;
  const num = parseInt(numEl.value) || 0;
  const parc = parseFloat(parcEl.value) || 0;

  const totalPago = num * parc;
  const acrescimo = totalPago - vista;
  const percAcrescimo = vista > 0 ? (acrescimo / vista) * 100 : 0;

  document.getElementById('preview-total')?.textContent && (
    document.getElementById('preview-total').textContent = `R$ ${totalPago.toFixed(2)}`
  );
  document.getElementById('preview-acrescimo')?.textContent && (
    document.getElementById('preview-acrescimo').textContent = `R$ ${acrescimo.toFixed(2)} (${percAcrescimo.toFixed(1)}%)`
  );

  const el = document.getElementById('preview-status');
  if (el) {
    if (vista <= 0 || num <= 0 || parc <= 0) {
      el.textContent = '—';
      el.className = 'fw-bold text-muted';
    } else if (acrescimo <= 0) {
      el.textContent = 'Sem acréscimo';
      el.className = 'fw-bold text-green';
    } else {
      el.textContent = 'Verificar após cálculo';
      el.className = 'fw-bold text-accent';
    }
  }
}

/* ---- Tooltips Bootstrap ---- */
function initTooltips() {
  document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => {
    new bootstrap.Tooltip(el);
  });
}

/* ---- Nav active state ---- */
function initNavActiveState() {
  const path = window.location.pathname;
  document.querySelectorAll('.navbar-agifora .nav-link').forEach(link => {
    if (link.getAttribute('href') === path) {
      link.classList.add('active');
    }
  });
}

/* ---- Utilitários ---- */
function showAlert(msg, type = 'info') {
  const div = document.createElement('div');
  div.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3`;
  div.style.zIndex = '9999';
  div.style.minWidth = '280px';
  div.innerHTML = `${msg}<button type="button" class="btn-close" data-bs-dismiss="alert"></button>`;
  document.body.appendChild(div);
  setTimeout(() => div.remove(), 3500);
}

function copyToClipboard(text) {
  navigator.clipboard.writeText(text).then(() => showAlert('Copiado!', 'success'));
}
