// ── Time ──
function updateTime() {
  const el = document.getElementById('page-time');
  const now = new Date();
  el.textContent = now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: true });
}
updateTime();
setInterval(updateTime, 10000);

// ── Navigation ──
function showPage(name, navEl) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  document.getElementById('page-' + name).classList.add('active');
  const activeNav = navEl || document.querySelector(`.nav-item[data-page="${name}"]`);
  if (activeNav) activeNav.classList.add('active');
  const titles = {
    test: 'Test',
    dashboard: 'Dashboard',
    cameras: 'Cameras',
    play: 'Play',
    activity: 'Activity',
    schedule: 'Schedule',
    reports: 'Reports',
    settings: 'Settings'
  };
  document.getElementById('page-title').textContent = titles[name] || name;
}

// ── Toast ──
function toast(msg, icon = '✓') {
  const wrap = document.getElementById('toasts');
  const t = document.createElement('div');
  t.className = 'toast';
  t.innerHTML = `<span>${icon}</span> ${msg}`;
  wrap.appendChild(t);
  setTimeout(() => {
    t.classList.add('out');
    setTimeout(() => t.remove(), 300);
  }, 2800);
}

function formatNumber(value, digits = 1) {
  const num = Number(value);
  return Number.isFinite(num) ? num.toFixed(digits) : '--';
}

function updateText(id, value) {
  const el = document.getElementById(id);
  if (el) el.textContent = value;
}

function updateFoodConsumption(foodConsumption) {
  if (!foodConsumption) return;

  updateText(
    'food-consumed-value',
    formatNumber(foodConsumption.session_total ?? foodConsumption.today_total)
  );
  updateText('food-today-value', formatNumber(foodConsumption.today_total));
  updateText('food-filtered-value', formatNumber(foodConsumption.filtered_value));
  updateText(
    'food-stability-value',
    foodConsumption.is_stable ? 'stable' : 'reading...'
  );

  if (foodConsumption.last_event) {
    const event = foodConsumption.last_event;
    updateText(
      'food-event-value',
      `Last event: ${formatNumber(event.consumed_amount)}g (${formatNumber(event.before_value)} -> ${formatNumber(event.after_value)})`
    );
  } else {
    updateText('food-event-value', 'No consumption event recorded yet');
  }
}

async function resetFoodConsumption() {
  try {
    const res = await fetch('/api/consumption/reset?sensor_type=food', {
      method: 'POST'
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.detail || 'Failed to reset counter');
    updateFoodConsumption(data.consumption?.sensors?.food);
    toast('Food test counter reset', '✓');
  } catch (err) {
    toast(err.message || 'Failed to reset counter', '⚠️');
  }
}

// ── Controls ──
async function toggleCtrl(btn) {
  const name = btn.querySelector('.ctrl-name').textContent;
  const state = btn.querySelector('.ctrl-state');

  const commandMap = {
    'LED':        'LED_TOGGLE',
    'Water Pump': 'PUMP_TOGGLE',
  };

  const command = commandMap[name];

  if (command) {
    // Optimistically update UI right away
    btn.classList.toggle('on');
    const isOn = btn.classList.contains('on');
    state.textContent = isOn ? 'On' : 'Off';
    toast(`${name} turned ${isOn ? 'on' : 'off'}`, '💡');

    try {
      const payload = { type: command };
      console.log('POST /api/command →', JSON.stringify(payload, null, 2));

      await fetch('/api/command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
    } catch (err) {
      // Revert UI if the request failed
      btn.classList.toggle('on');
      state.textContent = btn.classList.contains('on') ? 'On' : 'Off';
      toast(`Failed to toggle ${name}`, '⚠️');
    }
  } else {
    // UI-only buttons
    btn.classList.toggle('on');
    state.textContent = btn.classList.contains('on') ? 'On' : 'Off';
    toast(`${name} turned ${btn.classList.contains('on') ? 'on' : 'off'}`, '💡');
  }
}

async function refreshState() {
  try {
    const res = await fetch('/api/state');
    const data = await res.json();
    // Sync LED button
    // syncCtrlBtn('LED', data.led === 1);

    // Sync Water Pump button
    // syncCtrlBtn('Water Pump', data.pump === 1);

    const loadCellValue =
      data.weight ?? data.load ?? data.sensor?.weight ?? data.sensor?.load;

    // Update Test page load-cell widget
    const weightValue = document.getElementById('weight-value');
    if (weightValue && loadCellValue !== null && loadCellValue !== undefined) {
      weightValue.textContent = loadCellValue;
    }

    updateFoodConsumption(data.consumption?.sensors?.food);

  } catch (err) {
    console.error('Error loading state:', err);
  }
}

// Poll every second
refreshState();
setInterval(refreshState, 1000);

// ── Feed ──
function triggerFeed(btn) {
  const h = btn.querySelector('h3');
  const p = btn.querySelector('p');
  const a = btn.querySelector('.fa');
  btn.style.pointerEvents = 'none';
  h.textContent = 'Dispensing…';
  p.textContent = 'Portion on the way!';
  a.textContent = '⏳';
  setTimeout(() => {
    h.textContent = 'Mochi is eating!';
    p.textContent = '40g dispensed · Just now';
    a.textContent = '✓';
    a.style.color = 'var(--green)';
    toast('🍽 Mochi has been fed!');
    setTimeout(() => {
      h.textContent = 'Feed Mochi';
      p.textContent = 'Last fed just now';
      a.textContent = '→';
      a.style.color = '';
      btn.style.pointerEvents = '';
    }, 4000);
  }, 1600);
}

function setDispense(g) {
  document.getElementById('dispense-input').value = g;
}

function toggleLaserFromPlay() {
  if (controlActive) {
    deactivateControl();
  } else {
    activateControl();
  }
}

async function dispenseFood() {
  const grams = parseInt(document.getElementById('dispense-input').value);
  if (!grams || grams < 5 || grams > 150) {
    toast('Enter a valid amount (5–150g)', '⚠️');
    return;
  }

  const btn = document.getElementById('dispense-food-btn');
  btn.disabled = true;
  btn.textContent = '⏳ Dispensing…';

  try {
    const payload = { type: 'DISPENSE', params: {grams: grams}};
    console.log('POST /api/command →', JSON.stringify(payload, null, 2));

    await fetch('/api/command', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    toast(`🍽 Dispensing ${grams}g for Mochi!`);
  } catch (err) {
    toast('Failed to dispense', '⚠️');
    console.error(err);
  } finally {
    setTimeout(() => {
      btn.disabled = false;
      btn.innerHTML = '🍽 Dispense Now';
    }, 3000);
  }
}

let controlActive = false;
let laserX = 50; // percent
let laserY = 50;
const speedMap = { '🐌': 2, '🐈': 5, '⚡': 10 };
let moveSpeed = 5;

const keyMap = {
  'w': 'up',   'ArrowUp':    'up',
  's': 'down', 'ArrowDown':  'down',
  'a': 'left', 'ArrowLeft':  'left',
  'd': 'right','ArrowRight': 'right',
};

const keyElMap = {
  'w': 'key-w', 'ArrowUp':    'key-up',
  's': 'key-s', 'ArrowDown':  'key-down',
  'a': 'key-a', 'ArrowLeft':  'key-left',
  'd': 'key-d', 'ArrowRight': 'key-right',
};

async function activateControl() {
  controlActive = true;
  document.getElementById('focus-hint').style.display = 'none';
  document.getElementById('control-bar').style.display = 'flex';
  document.getElementById('laser-dot').style.display = 'block';
  document.getElementById('laser-active-badge').style.display = 'flex';

  try {
    const payload = { type: 'LASER_TOGGLE' };
    console.log('POST /api/command →', JSON.stringify(payload, null, 2));
    await fetch('/api/command', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
  } catch (err) {
    console.error('Failed to activate laser:', err);
  }

  toast('🎯 Laser control active — use WASD to move', '🎯');
}

function deactivateControl() {
  controlActive = false;
  document.getElementById('focus-hint').style.display = 'flex';
  document.getElementById('control-bar').style.display = 'none';
  document.getElementById('laser-dot').style.display = 'none';
  document.getElementById('laser-active-badge').style.display = 'none';
}

function selectSpeed(el) {
  document.querySelectorAll('.speed-btn').forEach(b => {
    b.classList.remove('selected');
    b.style.background = 'var(--surface2)';
    b.style.borderColor = 'var(--border)';
    b.style.color = 'var(--text-mid)';
  });
  el.classList.add('selected');
  el.style.background = 'var(--amber-glow)';
  el.style.borderColor = 'var(--border2)';
  el.style.color = 'var(--amber-l)';
  const icon = el.querySelector('span').textContent;
  moveSpeed = speedMap[icon] ?? 5;
}

document.addEventListener('keydown', (e) => {
  if (!controlActive) return;
  if (e.key === 'Escape') { deactivateControl(); return; }

  const dir = keyMap[e.key];
  if (!dir) return;
  e.preventDefault();

  // Highlight key cap
  const keyElId = keyElMap[e.key];
  if (keyElId) document.getElementById(keyElId)?.classList.add('pressed');

  // Move dot instantly
  if (dir === 'up')    laserY = Math.max(5,  laserY - moveSpeed);
  if (dir === 'down')  laserY = Math.min(95, laserY + moveSpeed);
  if (dir === 'left')  laserX = Math.max(5,  laserX - moveSpeed);
  if (dir === 'right') laserX = Math.min(95, laserX + moveSpeed);

  document.getElementById('laser-dot').style.left = laserX + '%';
  document.getElementById('laser-dot').style.top  = laserY + '%';

  // Send to backend — fire and forget, no await
  sendLaserMove(dir);
});

// Throttle — only send to backend at most every 50ms
let lastSent = 0;
function sendLaserMove(dir) {
  const now = Date.now();
  if (now - lastSent < 10) return;  // drop if too soon
  lastSent = now;

  const payload = { type: 'LASER_MOVE', params: { direction: dir, x: laserX, y: laserY } };
  console.log('POST /api/command →', JSON.stringify(payload, null, 2));

  fetch('/api/command', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  }).catch(err => console.error('Laser move failed:', err));
}

// document.addEventListener('keydown', async (e) => {
//   if (!controlActive) return;
//   if (e.key === 'Escape') { deactivateControl(); return; }

//   const dir = keyMap[e.key];
//   if (!dir) return;
//   e.preventDefault();

//   // Highlight key cap
//   const keyElId = keyElMap[e.key];
//   if (keyElId) document.getElementById(keyElId)?.classList.add('pressed');

//   // Move dot
//   if (dir === 'up')    laserY = Math.max(5,  laserY - moveSpeed);
//   if (dir === 'down')  laserY = Math.min(95, laserY + moveSpeed);
//   if (dir === 'left')  laserX = Math.max(5,  laserX - moveSpeed);
//   if (dir === 'right') laserX = Math.min(95, laserX + moveSpeed);

//   const dot = document.getElementById('laser-dot');
//   dot.style.left = laserX + '%';
//   dot.style.top  = laserY + '%';

//   // Send to backend
//   try {
//     const payload = { type: 'LASER_MOVE', params: { direction: dir, x: laserX, y: laserY } };
//     console.log('POST /api/command →', JSON.stringify(payload, null, 2));
//     await fetch('/api/command', {
//       method: 'POST',
//       headers: { 'Content-Type': 'application/json' },
//       body: JSON.stringify(payload)
//     });
//   } catch (err) {
//     console.error('Laser move failed:', err);
//   }
// });

document.addEventListener('keyup', (e) => {
  const keyElId = keyElMap[e.key];
  if (keyElId) document.getElementById(keyElId)?.classList.remove('pressed');
});

// ── Refresh stats ──
function refreshStats() {
  toast('Stats refreshed', '↻');
}
