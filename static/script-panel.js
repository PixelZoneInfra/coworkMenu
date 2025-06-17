// panel logic
let orders = [], prevCount = 0, pulse = null, alarmOn = true;
const POLL = 2000;
const ordersDiv = document.getElementById('orders');
const btn = document.getElementById('toggleAlarm');

btn.onclick = () => {
  alarmOn = false;
  stopPulse();
};

function randColor() {
  return `rgb(${[0,1,2].map(_=>Math.floor(Math.random()*256)).join(',')})`;
}
function startPulse() {
  if (!alarmOn || pulse) return;
  pulse = setInterval(() => {
    document.body.style.backgroundColor = randColor();
  }, 1000);
}
function stopPulse() {
  clearInterval(pulse);
  pulse = null;
  document.body.style.backgroundColor = 'white';
}

async function loadOrders() {
  const res = await fetch('/api/orders');
  orders = await res.json();
  render();
}

function render() {
  ordersDiv.innerHTML = '';
  orders.forEach(o => {
    const el = document.createElement('div');
    el.className = 'order';
    el.innerHTML = `
      <div><strong>#${o.id}</strong> biurko ${o.desk}: ${o.items}</div>
      <button data-id="${o.id}">Wydano</button>
    `;
    ordersDiv.appendChild(el);
    el.querySelector('button').onclick = async () => {
      await fetch(`/api/order/${o.id}`, { method: 'DELETE' });
      loadOrders();
    };
  });

  if (orders.length > prevCount) alarmOn = true;
  prevCount = orders.length;

  if (orders.length && alarmOn) startPulse();
  else stopPulse();
}

loadOrders();
setInterval(loadOrders, POLL);
