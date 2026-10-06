const API = '';
let session = null;
let custScope = 'me';
let orderScope = 'me';

const $ = (id) => document.getElementById(id);
const esc = (s) => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const isAdmin = () => session && session.role === 'admin';
const PLACEHOLDER = 'data:image/svg+xml;utf8,' + encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" width="300" height="180"><rect width="100%" height="100%" fill="#eef1f6"/><text x="50%" y="50%" fill="#9aa6b8" font-family="sans-serif" font-size="15" text-anchor="middle" dominant-baseline="middle">No image</text></svg>');
function toast(msg, kind) {
  const t = $('toast');
  t.textContent = msg;
  t.className = 'toast show ' + (kind || 'info');
  setTimeout(() => { t.className = 'toast ' + (kind || 'info'); }, 3200);
}

async function api(path, method, body) {
  const headers = { 'Content-Type': 'application/json' };
  if (session && session.token) headers['Authorization'] = 'Bearer ' + session.token;
  let res;
  try {
    res = await fetch(API + path, { method: method || 'GET', headers, body: body ? JSON.stringify(body) : undefined });
  } catch (e) {
    throw new Error('Could not reach the server. Please try again.');
  }
  const text = await res.text();
  let data = null;
  try { data = text ? JSON.parse(text) : null; } catch (e) { data = text; }
  if (!res.ok) {
    const detail = data && data.detail
      ? (typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail))
      : ('Request failed (HTTP ' + res.status + ')');
    throw new Error(detail);
  }
  return data;
}

function applySession(r) {
  session = { token: r.access_token, customer_id: r.customer_id, first_name: r.first_name, last_name: r.last_name, role: r.role };
  $('loginCard').classList.add('hidden');
  $('app').classList.remove('hidden');
  $('logoutBtn').classList.remove('hidden');
  $('whoami').textContent = 'Signed in as ' + r.first_name + ' ' + r.last_name + ' (id ' + r.customer_id + ')';
  $('adminBadge').style.display = isAdmin() ? 'inline-block' : 'none';
  custScope = isAdmin() ? 'all' : 'me';
  orderScope = isAdmin() ? 'all' : 'me';
  syncSeg('custScope', custScope);
  syncSeg('orderScope', orderScope);
  $('favWho').value = r.customer_id;
  loadProfile(); loadCustomers(); loadOrders(); loadFavorites();
}

function logout() {
  session = null;
  $('app').classList.add('hidden');
  $('logoutBtn').classList.add('hidden');
  $('loginCard').classList.remove('hidden');
  $('adminBadge').style.display = 'none';
  $('whoami').textContent = 'Not signed in';
}

async function doLogin() {
  const customer_id = parseInt($('loginId').value, 10);
  const email = $('loginEmail').value.trim();
  if (!customer_id || !email) { toast('Enter your id and email', 'err'); return; }
  try {
    const r = await api('/auth/login', 'POST', { customer_id, email });
    applySession(r);
    toast('Welcome, ' + r.first_name, 'ok');
  } catch (e) { toast(e.message, 'err'); }
}

async function doRegister() {
  const first_name = $('regFirst').value.trim();
  const last_name = $('regLast').value.trim();
  const email = $('regEmail').value.trim();
  const status = $('regStatus').value;
  if (!first_name || !last_name || !email) { toast('Fill in name and email', 'err'); return; }
  try {
    const r = await api('/auth/register', 'POST', { first_name, last_name, email, status });
    applySession(r);
    toast('Account created. Your customer id is ' + r.customer_id, 'ok');
  } catch (e) { toast(e.message, 'err'); }
}

async function loadProfile() {
  try {
    const c = await api('/customer/' + session.customer_id);
    $('pFirst').value = c.first_name; $('pLast').value = c.last_name;
    $('pEmail').value = c.email; $('pStatus').value = c.status;
  } catch (e) { toast(e.message, 'err'); }
}

async function saveProfile() {
  const body = { customer_id: session.customer_id, first_name: $('pFirst').value, last_name: $('pLast').value, email: $('pEmail').value, status: $('pStatus').value };
  try { await api('/customer/' + session.customer_id, 'PUT', body); toast('Profile saved', 'ok'); session.first_name = body.first_name; session.last_name = body.last_name; $('whoami').textContent = 'Signed in as ' + body.first_name + ' ' + body.last_name + ' (id ' + session.customer_id + ')'; loadCustomers(); }
  catch (e) { toast(e.message, 'err'); }
}

async function deleteProfile() {
  if (!confirm('Delete your account? This cannot be undone.')) return;
  try { await api('/customer/' + session.customer_id, 'DELETE'); toast('Account deleted', 'ok'); logout(); }
  catch (e) { toast(e.message, 'err'); }
}

async function loadCustomers() {
  try {
    let list = await api('/customer');
    if (custScope === 'me') list = list.filter(c => c.customer_id === session.customer_id);
    $('customersBody').innerHTML = list.map(c => {
      const mine = c.customer_id === session.customer_id;
      const reveal = mine || isAdmin();
      const st = (c.status || '').toLowerCase();
      const idCell = reveal ? (c.customer_id + (mine ? ' <span class="badge me">me</span>' : '')) : '<span class="muted">hidden</span>';
      const emailCell = reveal ? esc(c.email) : '<span class="muted">hidden</span>';
      return '<tr><td>' + idCell + '</td><td>' + esc(c.first_name) + ' ' + esc(c.last_name) + '</td><td>' + emailCell + '</td><td><span class="badge ' + st + '">' + esc(c.status) + '</span></td></tr>';
    }).join('') || '<tr><td colspan=4 class="empty">No customers</td></tr>';
  } catch (e) { toast(e.message, 'err'); }
}

async function loadOrders() {
  try {
    let list = await api('/order');
    let nameById = {};
    try {
      const custs = await api('/customer');
      custs.forEach(c => { nameById[c.customer_id] = (c.first_name + ' ' + c.last_name).trim(); });
    } catch (e) { toast('Could not load customer names: ' + e.message, 'err'); }
    if (orderScope === 'me') list = list.filter(o => o.customer_id === session.customer_id);
    $('ordersBody').innerHTML = list.map(o => {
      const mine = o.customer_id === session.customer_id;
      const canEdit = mine || isAdmin();
      const owner = nameById[o.customer_id] || ('Customer #' + o.customer_id);
      const idCell = esc(owner) + (mine ? ' <span class="badge me">me</span>' : '');
      const img = o.image_url || PLACEHOLDER;
      const imgCell = '<img class="thumb" src="' + esc(img) + '" alt="' + esc(o.item_name) + '" onerror="this.src=\'' + PLACEHOLDER + '\'"/>';
      const acts = canEdit
        ? '<div class="actions"><button class="btn secondary sm" onclick="editOrder(' + o.order_id + ',\'' + esc(o.item_name).replace(/'/g, "\\'") + '\')">Edit</button><button class="btn danger sm" onclick="delOrder(' + o.order_id + ')">Cancel</button></div>'
        : '<span class="muted">\u2014</span>';
      return '<tr><td>' + o.order_id + '</td><td>' + idCell + '</td><td>' + imgCell + '</td><td>' + esc(o.item_name) + '</td><td>' + (o.price != null ? '$' + o.price : '\u2014') + '</td><td>' + acts + '</td></tr>';
    }).join('') || '<tr><td colspan=6 class="empty">No orders</td></tr>';
  } catch (e) { toast(e.message, 'err'); }
}

async function searchItemByName() {
  lastItemSearch = { type: 'item', name: $('itemSearchName').value.trim(), seller: $('itemSearchSeller').value.trim() };
  const name = $('itemSearchName').value.trim();
  const seller = $('itemSearchSeller').value.trim();
  if (!name) { toast('Enter an item name', 'err'); return; }
  try {
    const query = '?item_name=' + encodeURIComponent(name) + (seller ? '&seller_name=' + encodeURIComponent(seller) : '');
    renderItem(await api('/item/by-name' + query));
  } catch (e) { toast('Item search failed: ' + e.message, 'err'); }
}

async function searchItemById() {
  const v = parseInt($('itemSearchId').value, 10);
  if (!v) { toast('Enter an item id', 'err'); return; }
  try { renderItem(await api('/item/' + v)); }
  catch (e) { toast('Item lookup failed: ' + e.message, 'err'); }
}

async function searchItemsBySellerName() {
  const seller = $('sellerSearchName').value.trim();
  lastItemSearch = { type: 'seller', seller };
  if (!seller) { toast('Enter a seller name', 'err'); return; }
  try {
    renderItems(await api('/item/by-seller-name?seller_name=' + encodeURIComponent(seller)), 'Items from seller: ' + seller);
  } catch (e) { toast('Seller item search failed: ' + e.message, 'err'); }
}

function favoriteButton(it) {
  const id = Number(it.item_id);
  const exists = favoriteItemIds.has(id);
  return exists
    ? '<button class="btn secondary sm" disabled>Already in favorites</button>'
    : '<button class="btn secondary sm" onclick="addSearchFavorite(' + id + ')">Add to Favorites</button>';
}

function itemCardHtml(it) {
  const img = it.image_url || PLACEHOLDER;
  return '<div class="item-card">' +
    '<img src="' + esc(img) + '" alt="' + esc(it.item_name) + '" onerror="this.src=\'' + PLACEHOLDER + '\'"/>' +
    '<div class="body"><div class="name">' + esc(it.item_name) + '</div>' +
    '<div class="price">$' + esc(it.price) + '</div>' +
    '<div class="meta">Item #' + esc(it.item_id) + ' · Seller #' + esc(it.seller_id) + '</div>' +
    '<div class="foot"><button class="btn sm" onclick="placeSearchedOrder(' + esc(it.item_id) + ',\'' + esc(it.item_name).replace(/'/g, "\\'") + '\')">Order Item</button>' +
    favoriteButton(it) + '</div></div></div>';
}

function renderItem(it) {
  $('itemResult').innerHTML = itemCardHtml(it);
}

function renderItems(items, title) {
  $('itemResult').innerHTML = (title ? '<h3>' + esc(title) + '</h3>' : '') +
    (items || []).map(itemCardHtml).join('') ||
    '<div class="empty">No matching items found.</div>';
}

async function addSearchFavorite(item_id) {
  try {
    await api('/customer-favorite-item/lookup/by-id', 'POST', { customer_id: session.customer_id, item_id });
    favoriteItemIds.add(Number(item_id));
    toast('Added to favorites', 'ok');
    searchItemsByCurrentResult();
    loadFavorites();
  } catch (e) {
    toast('Could not add favorite: ' + e.message, 'err');
    if (e.message.toLowerCase().includes('already exists')) {
      favoriteItemIds.add(Number(item_id));
      searchItemsByCurrentResult();
    }
  }
}

let lastItemSearch = null;
async function searchItemsByCurrentResult() {
  if (!lastItemSearch) return;
  if (lastItemSearch.type === 'item') {
    try {
      const query = '?item_name=' + encodeURIComponent(lastItemSearch.name) + (lastItemSearch.seller ? '&seller_name=' + encodeURIComponent(lastItemSearch.seller) : '');
      renderItem(await api('/item/by-name' + query));
    } catch (e) { toast('Could not refresh item result: ' + e.message, 'err'); }
  } else if (lastItemSearch.type === 'seller') {
    try { renderItems(await api('/item/by-seller-name?seller_name=' + encodeURIComponent(lastItemSearch.seller)), 'Items from seller: ' + lastItemSearch.seller); } catch (e) { toast('Could not refresh seller items: ' + e.message, 'err'); }
  }
}

async function placeSearchedOrder(item_id, item_name) {
  const customer = {
    customer_id: session.customer_id,
    first_name: session.first_name,
    last_name: session.last_name,
    email: $('pEmail').value || 'na@na.com',
    status: $('pStatus').value || 'REGULAR'
  };
  try {
    await api('/order', 'POST', { customer, order: { item_id, item_name } });
    toast('Order placed', 'ok');
    loadOrders();
  } catch (e) { toast(e.message, 'err'); }
}

async function createOrder() {
  const item_name = $('oItem').value.trim();
  if (!item_name) { toast('Enter an item name', 'err'); return; }
  const customer = { customer_id: session.customer_id, first_name: session.first_name, last_name: session.last_name, email: $('pEmail').value || 'na@na.com', status: $('pStatus').value || 'REGULAR' };
  try { await api('/order', 'POST', { customer, order: { item_name } }); toast('Order placed', 'ok'); $('oItem').value = ''; loadOrders(); }
  catch (e) { toast(e.message, 'err'); }
}

window.editOrder = async function (id, current) {
  const item_name = prompt('New item name:', current);
  if (item_name == null || !item_name.trim()) return;
  try { await api('/order/' + id, 'PUT', { order_id: id, item_name: item_name.trim() }); toast('Order updated', 'ok'); loadOrders(); }
  catch (e) { toast(e.message, 'err'); }
};

window.delOrder = async function (id) {
  if (!confirm('Cancel order ' + id + '?')) return;
  try { await api('/order/' + id, 'DELETE'); toast('Order cancelled', 'ok'); loadOrders(); }
  catch (e) { toast(e.message, 'err'); }
};

function favTarget() {
  const v = parseInt($('favWho').value, 10);
  return v || session.customer_id;
}

let favoriteItemIds = new Set();

async function loadFavorites() {
  const who = favTarget();
  const own = who === session.customer_id;
  $('favHint').textContent = own ? 'Showing your own favorites.' : ('Showing favorites of customer #' + who + (isAdmin() ? ' (admin view).' : '. You can only change your own.'));
  try {
    const r = await api('/customer-favorite-item?customer_id=' + who);
    const items = r.favorite_items || [];
    if (own) favoriteItemIds = new Set(items.map(f => Number((f.item_response || {}).item_id)).filter(Boolean));
    const canEdit = own || isAdmin();
    $('favItems').innerHTML = items.map(f => {
      const it = f.item_response || {};
      const img = it.image_url || PLACEHOLDER;
      const foot = canEdit ? '<div class="foot"><button class="btn danger sm" onclick="delFav(' + f.favorite_item_id + ')">Remove</button></div>' : '';
      return '<div class="item-card"><img src="' + esc(img) + '" onerror="this.src=\'' + PLACEHOLDER + '\'"/><div class="body"><div class="name">' + esc(it.item_name) + '</div><div class="price">$' + esc(it.price) + '</div><div class="meta">Seller #' + esc(it.seller_id) + ' \u00b7 fav #' + esc(f.favorite_item_id) + '</div></div>' + foot + '</div>';
    }).join('') || '<div class="empty">No favorites yet.</div>';
  } catch (e) { toast(e.message, 'err'); }
}

async function addFavByName() {
  const item_name = $('fName').value.trim();
  if (!item_name) { toast('Enter an item name', 'err'); return; }
  try { await api('/customer-favorite-item', 'POST', { customer_id: favTarget(), item_name }); toast('Added to favorites', 'ok'); $('fName').value = ''; loadFavorites(); }
  catch (e) { toast(e.message, 'err'); }
}

async function addFavById() {
  const item_id = parseInt($('fId').value, 10);
  if (!item_id) { toast('Enter an item id', 'err'); return; }
  try { await api('/customer-favorite-item/lookup/by-id', 'POST', { customer_id: favTarget(), item_id }); toast('Added to favorites', 'ok'); $('fId').value = ''; loadFavorites(); }
  catch (e) { toast(e.message, 'err'); }
}

window.delFav = async function (id) {
  if (!confirm('Remove favorite ' + id + '?')) return;
  try { await api('/customer-favorite-item/' + id, 'DELETE'); toast('Removed', 'ok'); loadFavorites(); }
  catch (e) { toast(e.message, 'err'); }
};

async function tvGet() {
  const id = parseInt($('tvId').value, 10);
  if (!id) { toast('Enter a show id', 'err'); return; }
  try {
    const s = await api('/tv_maze/shows/' + id);
    const img = s.tv_show_image_original_url || PLACEHOLDER;
    $('tvResult').innerHTML = '<div class="item-card" style="max-width:320px"><img src="' + esc(img) + '" onerror="this.src=\'' + PLACEHOLDER + '\'"/><div class="body"><div class="name">' + esc(s.tv_show_name) + '</div><div class="meta">' + esc(s.tv_show_language || '') + '</div><div class="meta">' + esc((s.tv_show_description || '').replace(/<[^>]+>/g, '').slice(0, 200)) + '</div></div></div>';
  } catch (e) { toast(e.message, 'err'); }
}

function switchTab(name) {
  document.querySelectorAll('.tab').forEach(t => t.classList.toggle('active', t.dataset.tab === name));
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.add('hidden'));
  $('tab-' + name).classList.remove('hidden');
}

function syncSeg(groupId, val) {
  document.querySelectorAll('#' + groupId + ' .seg').forEach(b => b.classList.toggle('active', b.dataset.scope === val));
}

function switchAuth(name) {
  document.querySelectorAll('.authtab').forEach(t => t.classList.toggle('active', t.dataset.auth === name));
  $('authLogin').classList.toggle('hidden', name !== 'login');
  $('authRegister').classList.toggle('hidden', name !== 'register');
}

document.addEventListener('DOMContentLoaded', () => {
  $('loginBtn').onclick = doLogin;
  $('registerBtn').onclick = doRegister;
  $('logoutBtn').onclick = logout;
  $('pSave').onclick = saveProfile;
  $('pDelete').onclick = deleteProfile;
  $('oCreate').onclick = createOrder;
  $('fAddName').onclick = addFavByName;
  $('fAddId').onclick = addFavById;
  $('favLoad').onclick = loadFavorites;
  $('tvGet').onclick = tvGet;
  $('itemSearchNameBtn').onclick = searchItemByName;
  $('itemSearchIdBtn').onclick = searchItemById;
  $('sellerSearchBtn').onclick = searchItemsBySellerName;
  document.querySelectorAll('.tab').forEach(t => t.onclick = () => switchTab(t.dataset.tab));
  document.querySelectorAll('.authtab').forEach(t => t.onclick = () => switchAuth(t.dataset.auth));
  document.querySelectorAll('#custScope .seg').forEach(b => b.onclick = () => { custScope = b.dataset.scope; syncSeg('custScope', custScope); loadCustomers(); });
  document.querySelectorAll('#orderScope .seg').forEach(b => b.onclick = () => { orderScope = b.dataset.scope; syncSeg('orderScope', orderScope); loadOrders(); });
});
