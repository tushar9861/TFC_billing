const firebaseConfig = {
    apiKey: "AIzaSyCu9Vx5hJ59tHYys8Zu1CZ3H120JBiTAuQ",
    authDomain: "tiwarisfriedchicken.firebaseapp.com",
    projectId: "tiwarisfriedchicken",
    storageBucket: "tiwarisfriedchicken.firebasestorage.app",
    messagingSenderId: "577738865286",
    appId: "1:577738865286:web:fea2f6d6dbdaec370eaf07"
};

// Initialize Firebase (Compat)
firebase.initializeApp(firebaseConfig);
const auth = firebase.auth();
const db = firebase.firestore();
const googleProvider = new firebase.auth.GoogleAuthProvider();

// UI Elements
const toastEl = document.getElementById('toast');
const authContainer = document.getElementById('auth-container');
const appContainer = document.getElementById('app-container');
const logoutBtn = document.getElementById('logout-btn');
const googleLoginBtn = document.getElementById('google-login-btn');

const ADMIN_EMAIL = "contact.tfcbalasore@gmail.com";

// --- UTILS ---
function showToast(msg, type='success') {
    toastEl.textContent = msg;
    toastEl.className = `toast ${type}`;
    toastEl.classList.remove('hidden');
    setTimeout(() => {
        toastEl.classList.add('hidden');
    }, 3000);
}

function showView(viewId) {
    document.querySelectorAll('.view-container').forEach(v => v.classList.remove('active-view', 'hidden'));
    document.querySelectorAll('.view-container').forEach(v => {
        if(v.id === viewId) v.classList.add('active-view');
        else v.classList.add('hidden');
    });
}

function switchTab(tabId, title) {
    document.querySelectorAll('.tab-view').forEach(t => t.classList.add('hidden'));
    document.getElementById(tabId).classList.remove('hidden');
    
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    document.querySelector(`.nav-item[data-target="${tabId}"]`).classList.add('active');
    
    document.getElementById('header-title-text').textContent = title;
}

// --- AUTH LOGIC ---
auth.onAuthStateChanged(user => {
    if (user) {
        if (user.email === ADMIN_EMAIL) {
            showView('app-container');
            initDashboard();
        } else {
            // Wrong account used
            auth.signOut().then(() => {
                showToast("Access Denied: You must use the official TFC Admin Gmail account.", "error");
            });
            showView('auth-container');
        }
    } else {
        showView('auth-container');
    }
});

googleLoginBtn.addEventListener('click', (e) => {
    e.preventDefault();
    googleProvider.setCustomParameters({
        prompt: 'select_account'
    });
    auth.signInWithPopup(googleProvider)
        .then((result) => {
            if (result.user.email === ADMIN_EMAIL) {
                showToast("Login successful!");
            }
        })
        .catch((error) => {
            showToast(error.message, "error");
        });
});

logoutBtn.addEventListener('click', () => {
    auth.signOut();
});

// --- APP LOGIC ---

document.querySelectorAll('.nav-item').forEach(nav => {
    nav.addEventListener('click', (e) => {
        e.preventDefault();
        const target = nav.getAttribute('data-target');
        const title = nav.getAttribute('data-title');
        switchTab(target, title);
    });
});

let liveOrdersUnsubscribe = null;
let billsUnsubscribe = null;

function initDashboard() {
    loadDashboardMetrics();
    setupLiveOrders();
    loadBills();
    loadCustomers();
    loadPOS();
}

function loadDashboardMetrics() {
    // Get today's start and end timestamps
    const now = new Date();
    const startOfDay = new Date(now.getFullYear(), now.getMonth(), now.getDate()).toISOString();
    
    db.collection('bills')
        .where('dt', '>=', startOfDay)
        .onSnapshot(snapshot => {
            let totalRev = 0;
            snapshot.forEach(doc => {
                totalRev += (doc.data().total_amount || doc.data().total || 0);
            });
            document.getElementById('metric-revenue').textContent = `₹${totalRev.toFixed(2)}`;
            document.getElementById('metric-sales').textContent = snapshot.size;
        });
}

function setupLiveOrders() {
    const ordersList = document.getElementById('live-orders-list');
    const badge = document.getElementById('orders-badge');
    let currentFilter = 'pending'; // 'pending' or 'preparing'
    
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentFilter = btn.getAttribute('data-filter');
            renderOrders();
        });
    });

    let ordersData = [];

    if (liveOrdersUnsubscribe) liveOrdersUnsubscribe();
    
    liveOrdersUnsubscribe = db.collection('web_orders')
        .where('status', 'in', ['pending', 'preparing'])
        .onSnapshot(snapshot => {
            ordersData = [];
            snapshot.forEach(doc => {
                ordersData.push({ id: doc.id, ...doc.data() });
            });
            
            // Sort by timestamp
            ordersData.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
            
            const pendingCount = ordersData.filter(o => o.status === 'pending').length;
            if (pendingCount > 0) {
                badge.textContent = pendingCount;
                badge.classList.remove('hidden');
            } else {
                badge.classList.add('hidden');
            }
            
            document.getElementById('metric-kots').textContent = ordersData.length;
            renderOrders();
        });

    function renderOrders() {
        const ordersList = document.getElementById('live-orders-list');
        if (!ordersList) return;
        
        try {
            ordersList.innerHTML = '';
            const filtered = ordersData.filter(o => o.status === currentFilter);
            
            if (filtered.length === 0) {
                ordersList.innerHTML = '<p style="text-align:center; color:#888; padding: 20px;">No orders here.</p>';
                return;
            }

            filtered.forEach(order => {
                const card = document.createElement('div');
                card.className = 'list-card';
                
                let parsedItems = order.items || [];
                if(typeof parsedItems === 'string') { try { parsedItems = JSON.parse(parsedItems); } catch(e) { parsedItems = []; } }
                let itemsHtml = (Array.isArray(parsedItems) ? parsedItems : []).map(i => `${i.qty}x ${i.name}`).join(', ');
                let timeAgo = Math.floor((new Date() - new Date(order.created_at)) / 60000);
                if (isNaN(timeAgo)) timeAgo = 0;
                
                card.innerHTML = `
                    <div class="card-header">
                        <span class="card-title">${order.customer_name || 'Guest'} <br><small>${order.customer_phone}</small></span>
                        <span class="card-badge badge-${order.status}">${order.status}</span>
                    </div>
                    <div class="card-body">
                        <p><strong>Order:</strong> ${itemsHtml}</p>
                        <p><strong>Total:</strong> ₹${order.total_amount || order.total || 0}</p>
                        <p><strong>Time:</strong> ${timeAgo} mins ago</p>
                    </div>
                    <div class="card-actions"></div>
                `;
                
                ordersList.appendChild(card);
                
                const actionsDiv = card.querySelector('.card-actions');
                if (order.status === 'pending') {
                    actionsDiv.innerHTML = `
                        <button class="btn-small btn-reject" onclick="updateOrderStatus('${order.id}', 'rejected')">Reject</button>
                        <button class="btn-small btn-accept" onclick="updateOrderStatus('${order.id}', 'preparing')">Accept</button>
                    `;
                } else if (order.status === 'preparing') {
                    actionsDiv.innerHTML = `
                        <button class="btn-small btn-ready" onclick="updateOrderStatus('${order.id}', 'ready')">Mark Ready</button>
                    `;
                }
            });
        } catch (err) {
            console.error(err);
            if(typeof showToast === 'function') { showToast('UI Error: ' + err.message, 'error'); }
        }
    }
}

window.updateOrderStatus = function(orderId, newStatus) {
    db.collection('web_orders').doc(orderId).update({
        status: newStatus,
        updated_at: new Date().toISOString()
    }).then(() => {
        showToast(`Order marked as ${newStatus}`);
    }).catch(err => {
        showToast(err.message, 'error');
    });
};

function loadBills() {
    const billsList = document.getElementById('bills-list');
    const searchInput = document.getElementById('bill-search');
    let allBills = [];

    db.collection('bills').orderBy('dt', 'desc').limit(50).onSnapshot(snapshot => {
        allBills = [];
        snapshot.forEach(doc => {
            allBills.push({ id: doc.id, ...doc.data() });
        });
        renderBills(allBills);
        renderCharts(allBills);
    });

    searchInput.addEventListener('input', (e) => {
        const q = e.target.value.toLowerCase();
        const filtered = allBills.filter(b => 
            (b.bill_no && b.bill_no.toLowerCase().includes(q)) || 
            (b.customer_name && b.customer_name.toLowerCase().includes(q))
        );
        renderBills(filtered);
    });

    function renderBills(bills) {
        billsList.innerHTML = '';
        if (bills.length === 0) {
            billsList.innerHTML = '<p style="text-align:center; color:#888; padding: 20px;">No bills found.</p>';
            return;
        }

        bills.forEach(bill => {
            const card = document.createElement('div');
            card.className = 'list-card';
            
            card.innerHTML = `
                <div class="card-header">
                    <span class="card-title">${bill.bill_no}</span>
                    <span style="font-weight:bold; color:var(--success);">₹${(bill.total_amount||bill.total||0).toFixed(2)}</span>
                </div>
                <div class="card-body">
                    <p><strong>Customer:</strong> ${bill.customer_name || 'Walk-in'}</p>
                    <p><strong>Date:</strong> ${bill.dt ? bill.dt.substring(0, 16) : 'N/A'}</p>
                    <p><strong>Type:</strong> ${bill.order_type || 'Takeaway'} - ${bill.payment_method || 'Cash'}</p>
                </div>
            `;
            billsList.appendChild(card);
        });
    }
}

function loadCustomers() {
    const custList = document.getElementById('customers-list');
    const searchInput = document.getElementById('customer-search');
    let allCust = [];

    db.collection('bills').orderBy('dt', 'desc').limit(100).get().then(snapshot => {
        const custMap = {};
        snapshot.forEach(doc => {
            const b = doc.data();
            if (b.phone && b.phone.length > 5) {
                if (!custMap[b.phone]) {
                    custMap[b.phone] = { phone: b.phone, name: b.customer_name, spent: 0, orders: 0 };
                }
                custMap[b.phone].spent += (b.total_amount || 0);
                custMap[b.phone].orders += 1;
            }
        });
        
        allCust = Object.values(custMap).sort((a, b) => b.spent - a.spent);
        renderCust(allCust);
    });

    searchInput.addEventListener('input', (e) => {
        const q = e.target.value.toLowerCase();
        const filtered = allCust.filter(c => 
            c.phone.includes(q) || (c.name && c.name.toLowerCase().includes(q))
        );
        renderCust(filtered);
    });

    function renderCust(customers) {
        custList.innerHTML = '';
        if (customers.length === 0) {
            custList.innerHTML = '<p style="text-align:center; color:#888; padding: 20px;">No customers found.</p>';
            return;
        }

        customers.forEach(c => {
            const card = document.createElement('div');
            card.className = 'list-card';
            
            card.innerHTML = `
                <div class="card-header">
                    <span class="card-title">${c.name || 'Unknown'}</span>
                    <span class="card-badge badge-completed">${c.orders} Orders</span>
                </div>
                <div class="card-body">
                    <p><strong>Phone:</strong> ${c.phone}</p>
                    <p><strong>Total Spent:</strong> ₹${c.spent.toFixed(2)}</p>
                </div>
            `;
            custList.appendChild(card);
        });
    }
}

// --- CHARTS LOGIC ---
let salesTrendChart = null;
let categoryPieChart = null;

function renderCharts(bills) {
    const ctxTrend = document.getElementById('salesTrendChart').getContext('2d');
    const ctxPie = document.getElementById('categoryPieChart').getContext('2d');
    
    const trendMap = {};
    const catMap = {};
    
    bills.forEach(b => {
        if (!b.dt) return;
        const d = b.dt.split(/[ T]/)[0];
        trendMap[d] = (trendMap[d] || 0) + (b.total_amount || b.total || 0);
        
        let items = [];
        try {
            items = typeof b.items === 'string' ? JSON.parse(b.items) : b.items;
        } catch(e) {
            items = b.items;
        }
        
        (items || []).forEach(i => {
            const cat = i.category || 'Other';
            catMap[cat] = (catMap[cat] || 0) + (i.qty || 1);
        });
    });
    
    const sortedDates = Object.keys(trendMap).sort();
    const trendLabels = sortedDates.slice(-7);
    const trendData = trendLabels.map(d => trendMap[d]);
    
    if(salesTrendChart) salesTrendChart.destroy();
    salesTrendChart = new Chart(ctxTrend, {
        type: 'line',
        data: {
            labels: trendLabels,
            datasets: [{
                label: 'Revenue (₹)',
                data: trendData,
                borderColor: '#e53e3e',
                tension: 0.3,
                fill: true,
                backgroundColor: 'rgba(229, 62, 62, 0.1)'
            }]
        },
        options: { responsive: true, maintainAspectRatio: false }
    });
    
    const catLabels = Object.keys(catMap);
    const catData = Object.values(catMap);
    
    if(categoryPieChart) categoryPieChart.destroy();
    categoryPieChart = new Chart(ctxPie, {
        type: 'pie',
        data: {
            labels: catLabels,
            datasets: [{
                data: catData,
                backgroundColor: ['#e53e3e', '#38a169', '#3182ce', '#d69e2e', '#805ad5', '#e53e3e']
            }]
        },
        options: { responsive: true, maintainAspectRatio: false }
    });
}

// --- POS LOGIC ---
let posProducts = [];
let posCart = [];
let currentPosCategory = 'All';

function loadPOS() {
    db.collection('products').onSnapshot(snapshot => {
        posProducts = [];
        const categories = new Set();
        categories.add('All');
        
        snapshot.forEach(doc => {
            const p = doc.data();
            p.id = doc.id;
            posProducts.push(p);
            if (p.category) categories.add(p.category);
        });
        
        renderPosCategories(Array.from(categories));
        renderPosProducts();
    });
    
    document.getElementById('pos-search').addEventListener('input', () => renderPosProducts());
    document.getElementById('pos-discount').addEventListener('input', updateCartTotals);
    
    document.getElementById('btn-generate-kot').addEventListener('click', generateKOT);
    document.getElementById('btn-finalize-bill').addEventListener('click', finalizeBill);
}

function renderPosCategories(cats) {
    const catContainer = document.getElementById('pos-categories');
    catContainer.innerHTML = '';
    cats.forEach(c => {
        const btn = document.createElement('button');
        btn.className = 'cat-btn' + (c === currentPosCategory ? ' active' : '');
        btn.textContent = c;
        btn.onclick = () => {
            currentPosCategory = c;
            document.querySelectorAll('.cat-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            renderPosProducts();
        };
        catContainer.appendChild(btn);
    });
}

function renderPosProducts() {
    const grid = document.getElementById('pos-products');
    grid.innerHTML = '';
    const search = document.getElementById('pos-search').value.toLowerCase();
    
    let filtered = posProducts.filter(p => {
        const matchesCat = currentPosCategory === 'All' || p.category === currentPosCategory;
        const matchesSearch = p.name && p.name.toLowerCase().includes(search);
        return matchesCat && matchesSearch;
    });
    
    filtered.forEach(p => {
        const card = document.createElement('div');
        card.className = 'prod-card';
        card.innerHTML = `
            <div class="prod-name">${p.name}</div>
            <div class="prod-price">₹${p.price}</div>
        `;
        card.onclick = () => addToCart(p);
        grid.appendChild(card);
    });
}

window.addToCart = function(prod) {
    const existing = posCart.find(i => i.id === prod.id);
    if (existing) {
        existing.qty += 1;
    } else {
        posCart.push({
            id: prod.id,
            name: prod.name,
            price: parseFloat(prod.price) || 0,
            qty: 1,
            category: prod.category
        });
    }
    renderCart();
};

window.updateCartQty = function(id, delta) {
    const item = posCart.find(i => i.id === id);
    if (item) {
        item.qty += delta;
        if (item.qty <= 0) {
            posCart = posCart.filter(i => i.id !== id);
        }
        renderCart();
    }
};

function renderCart() {
    const list = document.getElementById('pos-cart-items');
    list.innerHTML = '';
    
    if (posCart.length === 0) {
        list.innerHTML = '<p style="text-align:center; color:#888; padding: 20px;">Cart is empty.</p>';
    } else {
        posCart.forEach(item => {
            const div = document.createElement('div');
            div.className = 'cart-item';
            div.innerHTML = `
                <div class="cart-item-name">${item.name} <br><small>₹${item.price}</small></div>
                <div class="cart-item-controls">
                    <button class="qty-btn" onclick="updateCartQty('${item.id}', -1)">-</button>
                    <span>${item.qty}</span>
                    <button class="qty-btn" onclick="updateCartQty('${item.id}', 1)">+</button>
                </div>
            `;
            list.appendChild(div);
        });
    }
    updateCartTotals();
}

function updateCartTotals() {
    let subtotal = 0;
    posCart.forEach(i => subtotal += i.price * i.qty);
    
    const discount = parseFloat(document.getElementById('pos-discount').value || 0);
    const tax = (subtotal - discount) * 0.05;
    const total = subtotal - discount + tax;
    
    document.getElementById('pos-subtotal').textContent = '₹' + subtotal.toFixed(2);
    document.getElementById('pos-tax').textContent = '₹' + tax.toFixed(2);
    document.getElementById('pos-total').textContent = '₹' + total.toFixed(2);
}

function generateReceiptId(prefix) {
    const now = new Date();
    const ts = Math.floor(now.getTime() / 1000).toString().slice(-6);
    return prefix + ts;
}

function getLocalISOTime() {
    const tzoffset = (new Date()).getTimezoneOffset() * 60000;
    return (new Date(Date.now() - tzoffset)).toISOString().slice(0, 19).replace('T', ' ');
}

function generateKOT() {
    if (posCart.length === 0) {
        showToast("Cart is empty!", "error");
        return;
    }
    const kotNo = generateReceiptId('KOT-');
    const kotData = {
        kot_no: kotNo,
        customer_name: 'Web Admin Walkin',
        phone: '',
        items: posCart,
        dt: getLocalISOTime(),
        status: 'pending',
        source: 'web_admin'
    };
    
    db.collection('kots').doc(kotNo).set(kotData).then(() => {
        showToast("KOT Generated!");
        posCart = [];
        renderCart();
    }).catch(e => showToast(e.message, "error"));
}

function finalizeBill() {
    if (posCart.length === 0) {
        showToast("Cart is empty!", "error");
        return;
    }
    const billNo = generateReceiptId('INV-');
    
    let subtotal = 0;
    posCart.forEach(i => subtotal += i.price * i.qty);
    const discount = parseFloat(document.getElementById('pos-discount').value || 0);
    const tax = (subtotal - discount) * 0.05;
    const total = subtotal - discount + tax;
    
    let paymentMethod = 'Cash';
    const checkedInput = document.querySelector('input[name="payment_method"]:checked');
    if (checkedInput) paymentMethod = checkedInput.value;
    
    const billData = {
        bill_no: billNo,
        customer_name: 'Web Admin Walkin',
        phone: '',
        items: posCart,
        subtotal: subtotal,
        discount: discount,
        tax: tax,
        total_amount: total,
        payment_method: paymentMethod,
        order_type: 'Takeaway',
        dt: getLocalISOTime(),
        source: 'web_admin'
    };
    
    db.collection('bills').doc(billNo).set(billData).then(() => {
        showToast("Bill Finalized!");
        posCart = [];
        renderCart();
        document.getElementById('pos-discount').value = '';
    }).catch(e => showToast(e.message, "error"));
}
