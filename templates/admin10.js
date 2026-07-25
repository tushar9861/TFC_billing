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
    document.querySelectorAll('.tab-view').forEach(t => {
        t.classList.add('hidden');
        t.classList.remove('active-tab');
    });
    const target = document.getElementById(tabId);
    if(target) {
        target.classList.remove('hidden');
        target.classList.add('active-tab');
    }
    
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    document.querySelector(`.nav-item[data-target="${tabId}"]`).classList.add('active');
    
    document.getElementById('header-title-text').textContent = title;
}

// --- AUTH LOGIC ---

let currentUserRole = null;
auth.onAuthStateChanged(user => {
    if (user) {
        // Query users collection to check role
        db.collection('users').where('email', '==', user.email).limit(1).get().then(snapshot => {
            if (!snapshot.empty) {
                const userData = snapshot.docs[0].data();
                currentUserRole = userData.role || 'cashier'; // default to cashier if no role
                
                // If kitchen staff, only show KDS
                if (currentUserRole === 'kitchen') {
                    document.querySelectorAll('.nav-item').forEach(el => el.style.display = 'none');
                    document.querySelector('.nav-item[data-target="view-kds"]').style.display = 'flex';
                    switchTab('view-kds', 'Kitchen Display (KDS)');
                } else if (currentUserRole === 'cashier') {
                    // Hide reports, expenses, users, etc.
                    document.querySelectorAll('.nav-item').forEach(el => {
                        const target = el.getAttribute('data-target');
                        if (['view-reports', 'view-expenses', 'view-procurement', 'view-inventory'].includes(target)) {
                            el.style.display = 'none';
                        }
                    });
                    switchTab('view-pos', 'POS / Billing');
                } else {
                    // Super Admin / Manager gets everything
                    document.querySelectorAll('.nav-item').forEach(el => el.style.display = 'flex');
                    if (typeof loadDashboard === "function") loadDashboard();
                    if (typeof initDashboard === "function") initDashboard();
                }
                
                showView('app-container');
            } else {
                // If not found in users collection, allow if Super Admin
                if (user.email === ADMIN_EMAIL) {
                    currentUserRole = 'super_admin';
                    document.querySelectorAll('.nav-item').forEach(el => el.style.display = 'flex');
                    if (typeof loadDashboard === "function") loadDashboard();
                    if (typeof initDashboard === "function") initDashboard();
                    showView('app-container');
                } else {
                    auth.signOut().then(() => {
                        showToast("Access Denied: Staff account not found.", "error");
                    });
                    showView('auth-container');
                }
            }
        }).catch(err => {
            console.error(err);
            if (user.email === ADMIN_EMAIL) {
                showView('app-container');
            }
        });
    } else {
        showView('auth-container');
    }
});

const loginBtn = document.getElementById('admin-login-btn');
const pwdInput = document.getElementById('admin-pwd-input');

function handleLogin(e) {
    if(e) e.preventDefault();
    const emailInput = document.getElementById('admin-email-input');
    const email = emailInput ? emailInput.value.trim() : ADMIN_EMAIL;
    const pwd = pwdInput.value;
    
    if (!email || !pwd) {
        showToast("Please enter email and password", "error");
        return;
    }
    
    const originalText = loginBtn.innerHTML;
    loginBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Authenticating...';
    
    auth.signInWithEmailAndPassword(email, pwd)
        .then(() => {
            loginBtn.innerHTML = originalText;
            showToast("Login successful!");
        })
        .catch((error) => {
            loginBtn.innerHTML = originalText;
            console.error("Firebase Auth Error: ", error);
            showToast("Auth Error: " + error.message, "error");
        });
}

if (loginBtn && pwdInput) {
    loginBtn.addEventListener('click', handleLogin);
    pwdInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            handleLogin(e);
        }
    });
}

logoutBtn.addEventListener('click', () => {
    auth.signOut();
});

// --- APP LOGIC ---

// Hamburger Toggle
const hamburgerBtn = document.getElementById('hamburger-btn');
const closeSidebarBtn = document.getElementById('close-sidebar-btn');
const sidebar = document.getElementById('main-sidebar');

if (hamburgerBtn) {
    hamburgerBtn.addEventListener('click', () => {
        sidebar.classList.add('open');
    });
}
if (closeSidebarBtn) {
    closeSidebarBtn.addEventListener('click', () => {
        sidebar.classList.remove('open');
    });
}

document.querySelectorAll('.nav-item').forEach(nav => {
    nav.addEventListener('click', (e) => {
        e.preventDefault();
        const target = nav.getAttribute('data-target');
        const title = nav.getAttribute('data-title');
        
        // Ensure nav element actually exists (it may not if it's a skeleton view)
        const targetEl = document.getElementById(target);
        if(targetEl) {
            switchTab(target, title);
        } else {
            showToast(title + " is not yet fully implemented.", "error");
        }
        
        // Auto-close sidebar on mobile
        if(window.innerWidth <= 768 && sidebar) {
            sidebar.classList.remove('open');
        }
    });
});

let liveOrdersUnsubscribe = null;
let billsUnsubscribe = null;
let dashboardInitialized = false;

function initDashboard() {
    if (dashboardInitialized) return;
    dashboardInitialized = true;
    loadDashboardMetrics();
    setupLiveOrders();
    loadBills();
    loadCustomers();
    loadPOS();
    setupRestaurantStatus();
}

function loadDashboardMetrics() {
    const now = new Date();
    // Use ISO string for comparisons, but truncate to just YYYY-MM-DD to be safe if 'dt' formats vary.
    // Actually ISO format YYYY-MM-DDTHH:mm:ss works fine with firestore string comparison if they match exactly.
    const pad = n => n.toString().padStart(2, '0');
    const startOfDay = `${now.getFullYear()}-${pad(now.getMonth()+1)}-${pad(now.getDate())}`;
    const startOfMonth = `${now.getFullYear()}-${pad(now.getMonth()+1)}-01`;

    let todayGrossSales = 0;
    let todayOrders = 0;
    let monthlySales = 0;
    
    // Bills
    db.collection('bills')
        .where('dt', '>=', startOfMonth)
        .onSnapshot(snapshot => {
            monthlySales = 0;
            todayGrossSales = 0;
            todayOrders = 0;
            
            let itemCounts = {};
            let uniqueCustomers = new Set();
            
            snapshot.forEach(doc => {
                const data = doc.data();
                const total = parseFloat(data.total_amount || data.total || data.grand_total || 0);
                const dt = data.dt || "";
                
                monthlySales += total;
                
                if (data.phone && data.phone !== "N/A" && data.phone !== "") {
                    uniqueCustomers.add(data.phone);
                }
                
                if (dt >= startOfDay) {
                    todayGrossSales += total;
                    todayOrders++;
                    
                    // Top seller tally
                    if(data.items) {
                        let itemsArr = data.items;
                        try {
                            if(typeof itemsArr === 'string') itemsArr = JSON.parse(itemsArr);
                            itemsArr.forEach(i => {
                                itemCounts[i.name] = (itemCounts[i.name] || 0) + (i.qty || 1);
                            });
                        } catch(e) {}
                    }
                }
            });
            
            document.getElementById('metric-customers').textContent = uniqueCustomers.size;
            
            let topSeller = "N/A";
            let maxCount = 0;
            for(let item in itemCounts) {
                if(itemCounts[item] > maxCount) {
                    maxCount = itemCounts[item];
                    topSeller = item;
                }
            }
            document.getElementById('metric-top-seller').textContent = topSeller;
            
            updateSalesUI();
            updateProfitUI();
        });

    let todayRefunds = 0;
    let monthlyRefunds = 0;
    // Refunds
    db.collection('refunds')
        .where('dt', '>=', startOfMonth)
        .onSnapshot(snapshot => {
            todayRefunds = 0;
            monthlyRefunds = 0;
            snapshot.forEach(doc => {
                const amt = parseFloat(doc.data().amount || 0);
                monthlyRefunds += amt;
                if((doc.data().dt || "") >= startOfDay) {
                    todayRefunds += amt;
                }
            });
            document.getElementById('metric-refunds').textContent = '₹' + todayRefunds.toFixed(2);
            updateSalesUI();
            updateProfitUI();
        });
        
    let monthlyExpenses = 0;
    // Expenses
    db.collection('expenses')
        .where('date', '>=', startOfMonth)
        .onSnapshot(snapshot => {
            monthlyExpenses = 0;
            snapshot.forEach(doc => {
                monthlyExpenses += parseFloat(doc.data().amount || 0);
            });
            updateProfitUI();
        });

    function updateSalesUI() {
        const netSales = todayGrossSales - todayRefunds;
        const avg = todayOrders > 0 ? (todayGrossSales / todayOrders) : 0;
        
        document.getElementById('metric-sales').textContent = '₹' + netSales.toFixed(2);
        document.getElementById('metric-orders').textContent = todayOrders;
        document.getElementById('metric-avg-bill').textContent = '₹' + avg.toFixed(2);
    }
    
    function updateProfitUI() {
        const netProfit = monthlySales - monthlyRefunds - monthlyExpenses;
        document.getElementById('metric-profit').textContent = '₹' + netProfit.toFixed(2);
    }
    
    // Low Stock
    db.collection('products')
        .onSnapshot(snapshot => {
            let lowStock = 0;
            snapshot.forEach(doc => {
                const data = doc.data();
                if(data.qty <= 5 && !data.is_combo) lowStock++;
            });
            document.getElementById('metric-inventory').textContent = lowStock;
        });
        
    // Pending Orders
    db.collection('web_orders')
        .where('status', 'in', ['pending', 'preparing'])
        .onSnapshot(snapshot => {
            document.getElementById('metric-pending').textContent = snapshot.size;
            document.getElementById('sidebar-orders-badge').textContent = snapshot.size;
            if(snapshot.size > 0) {
                document.getElementById('sidebar-orders-badge').classList.remove('hidden');
            } else {
                document.getElementById('sidebar-orders-badge').classList.add('hidden');
            }
        });
}

let adminOrdersData = {};
window.adminOrdersData = adminOrdersData;

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
            
            if (typeof window.previousPendingCount === 'undefined') window.previousPendingCount = 0;
            if (pendingCount > window.previousPendingCount) {
                const sound = document.getElementById('order-sound');
                if(sound) sound.play().catch(e => console.log('Audio play prevented:', e));
            }
            window.previousPendingCount = pendingCount;
            
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
                        <button class="btn-small" style="background: #3498db; color: white;" onclick="sendOrderToPOS('${order.id}')">Settle Bill</button>
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
    let updateData = {
        status: newStatus,
        updated_at: new Date().toISOString()
    };
    
    if (newStatus === 'rejected') {
        const reason = prompt('Please enter a reason for rejecting this order (e.g. Out of stock, Closing soon):');
        if (reason === null) return; // User cancelled
        updateData.rejection_reason = reason || 'No reason provided';
    }

    db.collection('web_orders').doc(orderId).update(updateData).then(() => {
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
        const isOut = p.is_active === false;
        
        card.innerHTML = `
            <div class="prod-name" style="${isOut ? 'text-decoration: line-through; color: #888;' : ''}">${p.name}</div>
            <div class="prod-price" style="${isOut ? 'color: #888;' : ''}">₹${p.price}</div>
            <div class="prod-toggle" style="margin-top: 10px;" onclick="event.stopPropagation()">
                <label class="switch" style="position: relative; display: inline-block; width: 34px; height: 18px;">
                    <input type="checkbox" onchange="toggleProductStatus('${p.id}', this.checked)" ${!isOut ? 'checked' : ''} style="opacity: 0; width: 0; height: 0;">
                    <span class="slider round" style="position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: #ccc; transition: .4s; border-radius: 24px;"></span>
                </label>
                <span style="font-size: 11px; vertical-align: top; margin-left: 5px;">${!isOut ? 'In Stock' : 'Out'}</span>
            </div>
        `;
        
        card.onclick = () => {
            if (p.is_active === false) {
                showToast("Item is out of stock!", "error");
                return;
            }
            addToCart(p);
        };
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
    const taxRate = typeof globalSettings !== "undefined" && globalSettings.tax_rate ? parseFloat(globalSettings.tax_rate) : 5;
    const tax = (subtotal - discount) * (taxRate / 100);
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
    const taxRate = typeof globalSettings !== "undefined" && globalSettings.tax_rate ? parseFloat(globalSettings.tax_rate) : 5;
    const tax = (subtotal - discount) * (taxRate / 100);
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
        if (window.printWebReceipt) window.printWebReceipt(billData);
        showToast("Bill Finalized!");
        posCart = [];
        renderCart();
        document.getElementById('pos-discount').value = '';
    }).catch(e => showToast(e.message, "error"));
}

window.finishOrder = function(orderId) {
    if (!adminOrdersData[orderId]) {
        showToast("Order details not found!", "error");
        return;
    }
    const o = adminOrdersData[orderId];
    db.collection('orders').doc(orderId).update({
        status: 'ready'
    }).then(() => {
        showToast("Order marked as ready!");
        posCart = [];
        if (o.items && Array.isArray(o.items)) {
            o.items.forEach(item => {
                posCart.push({
                    id: item.id || Math.random().toString(36).substr(2, 9),
                    name: item.name,
                    price: item.price,
                    qty: item.qty
                });
            });
        }
        document.getElementById('pos-customer-name').value = o.customer_name || '';
        document.getElementById('pos-customer-phone').value = o.phone || '';
        
        const posTab = document.querySelector('.nav-item[data-target="pos-tab"]');
        if (posTab) posTab.click();
        
        updateCartTotals();
        renderCart();
    }).catch(err => {
        showToast("Failed to update status: " + err.message, "error");
    });
};

// --- RESTAURANT STATUS TOGGLE ---
function setupRestaurantStatus() {
    const statusCheckbox = document.getElementById('restaurant-status-checkbox');
    const statusText = document.getElementById('restaurant-status-text');
    
    db.doc('metadata/settings').onSnapshot(doc => {
        if (doc.exists) {
            const isOnline = doc.data().is_online !== false;
            statusCheckbox.checked = isOnline;
            statusText.textContent = isOnline ? 'Online' : 'Offline';
            statusText.className = isOnline ? 'rest-online' : 'rest-offline';
        } else {
            db.doc('metadata/settings').set({ is_online: true }, { merge: true });
        }
    });
    
    statusCheckbox.addEventListener('change', (e) => {
        const isOnline = e.target.checked;
        statusText.textContent = isOnline ? 'Online' : 'Offline';
        statusText.className = isOnline ? 'rest-online' : 'rest-offline';
        db.doc('metadata/settings').set({ is_online: isOnline }, { merge: true })
            .then(() => showToast('Restaurant is now ' + (isOnline ? 'Online' : 'Offline')))
            .catch(err => showToast('Failed to update status: ' + err.message, 'error'));
    });
}


window.toggleProductStatus = function(id, isActive) {
    db.collection('products').doc(id).update({ is_active: isActive })
        .then(() => showToast("Item marked as " + (isActive ? 'In Stock' : 'Out of Stock')))
        .catch(err => showToast('Failed to update item: ' + err.message, 'error'));
};


// --- INVENTORY MANAGEMENT ---
function renderInventoryList() {
    const list = document.getElementById('inventory-list');
    if (!list) return;
    list.innerHTML = '';
    const search = (document.getElementById('inventory-search').value || '').toLowerCase();
    
    posProducts.filter(p => (p.name || '').toLowerCase().includes(search)).forEach(p => {
        const isOut = p.is_active === false;
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td style="font-weight: 600;">${p.name}</td>
            <td><span style="background: #e9ecef; padding: 4px 8px; border-radius: 6px; font-size: 12px;">${p.category || 'N/A'}</span></td>
            <td>₹${p.price}</td>
            <td>
                <span class="status-badge ${!isOut ? 'status-active' : 'status-inactive'}">${!isOut ? 'Active' : 'Inactive'}</span>
            </td>
            <td style="text-align: right;">
                <button class="icon-btn" onclick="editProduct('${p.id}')" style="color: var(--primary-color);"><i class="fas fa-edit"></i></button>
            </td>
        `;
        list.appendChild(tr);
    });
}

document.getElementById('inventory-search')?.addEventListener('input', renderInventoryList);

window.editProduct = function(id) {
    const p = posProducts.find(x => x.id === id);
    if(p) {
        document.getElementById('prod-name-input').value = p.name;
        document.getElementById('prod-cat-input').value = p.category || '';
        document.getElementById('prod-price-input').value = p.price;
        document.getElementById('save-product-btn').onclick = () => saveProduct(id);
        document.getElementById('product-modal').classList.remove('hidden');
    }
};

document.getElementById('add-product-btn')?.addEventListener('click', () => {
    document.getElementById('prod-name-input').value = '';
    document.getElementById('prod-cat-input').value = '';
    document.getElementById('prod-price-input').value = '';
    document.getElementById('save-product-btn').onclick = () => saveProduct(null);
    document.getElementById('product-modal').classList.remove('hidden');
});

function saveProduct(id) {
    const name = document.getElementById('prod-name-input').value.trim();
    const cat = document.getElementById('prod-cat-input').value.trim();
    const price = parseFloat(document.getElementById('prod-price-input').value);
    
    if(!name || isNaN(price)) {
        showToast('Please enter valid name and price', 'error');
        return;
    }
    
    const data = { name, category: cat, price, is_active: true };
    
    let req;
    if(id) {
        req = db.collection('products').doc(id).update(data);
    } else {
        data.id = 'PROD' + Date.now();
        req = db.collection('products').doc(data.id).set(data);
    }
    
    req.then(() => {
        showToast('Product saved successfully');
        document.getElementById('product-modal').classList.add('hidden');
    }).catch(e => showToast(e.message, 'error'));
}

const originalRenderPosProducts = window.renderPosProducts;
window.renderPosProducts = function() {
    if(originalRenderPosProducts) originalRenderPosProducts();
    if(document.getElementById('view-inventory').classList.contains('active-tab')) {
        renderInventoryList();
    }
};


// --- EXPENSES MANAGEMENT ---
let adminExpenses = [];
function loadExpenses() {
    db.collection('expenses').orderBy('date', 'desc').limit(100).onSnapshot(snap => {
        adminExpenses = [];
        let total = 0;
        snap.forEach(doc => {
            const data = doc.data();
            adminExpenses.push({id: doc.id, ...data});
            total += parseFloat(data.amount || 0);
        });
        document.getElementById('total-expenses-display').textContent = '₹' + total.toFixed(2);
        renderExpenses();
    });
}

function renderExpenses() {
    const list = document.getElementById('expenses-list');
    if(!list) return;
    list.innerHTML = '';
    const search = (document.getElementById('expense-search').value || '').toLowerCase();
    
    adminExpenses.filter(e => (e.description || '').toLowerCase().includes(search) || (e.category || '').toLowerCase().includes(search)).forEach(e => {
        const tr = document.createElement('tr');
        const dt = e.date ? new Date(e.date).toLocaleDateString() : '';
        tr.innerHTML = `
            <td>${dt}</td>
            <td><span style="background: #e9ecef; padding: 4px 8px; border-radius: 6px; font-size: 12px;">${e.category}</span></td>
            <td>${e.description}</td>
            <td style="text-align: right; font-weight: 700; color: #dc3545;">₹${parseFloat(e.amount).toFixed(2)}</td>
        `;
        list.appendChild(tr);
    });
}

document.getElementById('expense-search')?.addEventListener('input', renderExpenses);

document.getElementById('add-expense-btn')?.addEventListener('click', () => {
    document.getElementById('exp-amount-input').value = '';
    document.getElementById('exp-desc-input').value = '';
    document.getElementById('expense-modal').classList.remove('hidden');
});

document.getElementById('save-expense-btn')?.addEventListener('click', () => {
    const amount = parseFloat(document.getElementById('exp-amount-input').value);
    const cat = document.getElementById('exp-cat-input').value;
    const desc = document.getElementById('exp-desc-input').value.trim();
    
    if(isNaN(amount) || !desc) {
        showToast('Please enter valid amount and description', 'error');
        return;
    }
    
    db.collection('expenses').add({
        amount: amount,
        category: cat,
        description: desc,
        date: new Date().toISOString()
    }).then(() => {
        showToast('Expense logged successfully');
        document.getElementById('expense-modal').classList.add('hidden');
    }).catch(e => showToast(e.message, 'error'));
});

// Setup hook to load expenses when tab is clicked
let originalSwitchTab = switchTab;
switchTab = function(viewId, title) {
    if(originalSwitchTab) originalSwitchTab(viewId, title);
    
    if(viewId === 'view-inventory') {
        renderInventoryList();
    } else if (viewId === 'view-expenses') {
        loadExpenses();
    }
};


// --- PROCUREMENT MANAGEMENT ---
let adminPOs = [];
function loadProcurement() {
    db.collection('purchase_orders').orderBy('dt', 'desc').limit(100).onSnapshot(snap => {
        adminPOs = [];
        snap.forEach(doc => {
            adminPOs.push({id: doc.id, ...doc.data()});
        });
        renderProcurement();
    });
}

function renderProcurement() {
    const list = document.getElementById('procurement-list');
    if(!list) return;
    list.innerHTML = '';
    const search = (document.getElementById('po-search').value || '').toLowerCase();
    
    adminPOs.filter(po => (po.id || '').toLowerCase().includes(search) || (po.vendor_name || '').toLowerCase().includes(search)).forEach(po => {
        const tr = document.createElement('tr');
        const dt = po.dt ? new Date(po.dt).toLocaleDateString() : '';
        const isRec = po.status === 'Received';
        tr.innerHTML = `
            <td style="font-weight: 600;">${po.po_no || po.id}</td>
            <td>${dt}</td>
            <td>${po.vendor_name || 'N/A'}</td>
            <td>
                <span class="status-badge ${isRec ? 'status-active' : 'status-inactive'}" style="${!isRec ? 'background: #fff3cd; color: #856404;' : ''}">${po.status || 'Pending'}</span>
            </td>
            <td style="text-align: right; font-weight: 600;">₹${parseFloat(po.total_amount || 0).toFixed(2)}</td>
        `;
        list.appendChild(tr);
    });
}

document.getElementById('po-search')?.addEventListener('input', renderProcurement);

// Add PO Modal HTML injected dynamically to keep admin.html clean
const poModalHTML = `
<div id="po-modal" class="modal hidden" style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 2000; display: flex; align-items: center; justify-content: center;">
    <div style="background: white; width: 90%; max-width: 500px; border-radius: 12px; padding: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.2);">
        <h3 style="margin-bottom: 15px; font-size: 18px;">Create Purchase Order</h3>
        <div class="input-group" style="margin-bottom: 15px;">
            <label style="display: block; margin-bottom: 5px; font-size: 13px; color: var(--text-muted);">Vendor Name</label>
            <input type="text" id="po-vendor-input" style="width: 100%; padding: 10px; border: 1px solid var(--border-color); border-radius: 8px;">
        </div>
        <div class="input-group" style="margin-bottom: 15px;">
            <label style="display: block; margin-bottom: 5px; font-size: 13px; color: var(--text-muted);">Total Cost (₹)</label>
            <input type="number" id="po-total-input" style="width: 100%; padding: 10px; border: 1px solid var(--border-color); border-radius: 8px;">
        </div>
        <div class="input-group" style="margin-bottom: 20px;">
            <label style="display: block; margin-bottom: 5px; font-size: 13px; color: var(--text-muted);">Items/Notes</label>
            <textarea id="po-notes-input" rows="3" style="width: 100%; padding: 10px; border: 1px solid var(--border-color); border-radius: 8px; resize: none;"></textarea>
        </div>
        <div style="display: flex; justify-content: flex-end; gap: 10px;">
            <button class="btn-secondary" onclick="document.getElementById('po-modal').classList.add('hidden')" style="padding: 10px 15px; border-radius: 8px; border: 1px solid var(--border-color); background: white; cursor: pointer;">Cancel</button>
            <button class="btn-primary" id="save-po-btn" style="padding: 10px 15px; border-radius: 8px;">Save PO</button>
        </div>
    </div>
</div>
`;
document.body.insertAdjacentHTML('beforeend', poModalHTML);

document.getElementById('add-po-btn')?.addEventListener('click', () => {
    document.getElementById('po-vendor-input').value = '';
    document.getElementById('po-total-input').value = '';
    document.getElementById('po-notes-input').value = '';
    document.getElementById('po-modal').classList.remove('hidden');
});

document.getElementById('save-po-btn')?.addEventListener('click', () => {
    const vendor = document.getElementById('po-vendor-input').value.trim();
    const total = parseFloat(document.getElementById('po-total-input').value);
    const notes = document.getElementById('po-notes-input').value.trim();
    
    if(!vendor || isNaN(total)) {
        showToast('Please enter vendor and total cost', 'error');
        return;
    }
    
    const poNo = 'PO-' + Date.now().toString().slice(-6);
    db.collection('purchase_orders').doc(poNo).set({
        po_no: poNo,
        vendor_name: vendor,
        total_amount: total,
        items_desc: notes,
        status: 'Pending',
        dt: new Date().toISOString()
    }).then(() => {
        showToast('Purchase Order Created');
        document.getElementById('po-modal').classList.add('hidden');
    }).catch(e => showToast(e.message, 'error'));
});

// Update switchTab hook to include procurement
let originalSwitchTab2 = switchTab;
switchTab = function(viewId, title) {
    if(originalSwitchTab2) originalSwitchTab2(viewId, title);
    if(viewId === 'view-procurement') {
        loadProcurement();
    }
};

// --- BILLS & INVOICES MANAGEMENT ---
let adminBills = [];
function loadBills() {
    db.collection('bills').orderBy('dt', 'desc').limit(150).onSnapshot(snap => {
        adminBills = [];
        snap.forEach(doc => {
            adminBills.push({id: doc.id, ...doc.data()});
        });
        renderBillsList();
    });
}

function renderBillsList() {
    const list = document.getElementById('bills-list');
    if(!list) return;
    list.innerHTML = '';
    const search = (document.getElementById('bill-search').value || '').toLowerCase();
    
    adminBills.filter(b => (b.bill_no || b.id || '').toLowerCase().includes(search) || (b.customer_name || '').toLowerCase().includes(search) || (b.phone || '').includes(search)).forEach(b => {
        const tr = document.createElement('tr');
        const dt = b.dt ? new Date(b.dt).toLocaleString() : '';
        const name = b.customer_name || 'Walk-in';
        const phone = b.phone ? `<br><small style="color:var(--text-muted)">${b.phone}</small>` : '';
        tr.innerHTML = `
            <td style="font-weight: 600;">${b.bill_no || b.id}</td>
            <td style="font-size: 13px;">${dt}</td>
            <td>${name}${phone}</td>
            <td><span style="background: #e9ecef; padding: 4px 8px; border-radius: 6px; font-size: 12px;">${b.payment_method || 'Cash'}</span></td>
            <td style="text-align: right; font-weight: 700; color: var(--primary-color);">₹${parseFloat(b.total_amount || 0).toFixed(2)}</td>
            <td style="text-align: center;">
                <button class="icon-btn" onclick="viewBillDetails('${b.id}')" style="color: #007bff; background: rgba(0,123,255,0.1); border-radius: 6px; padding: 4px 8px; font-size: 13px;"><i class="fas fa-eye"></i> View</button>
            </td>
        `;
        list.appendChild(tr);
    });
}

document.getElementById('bill-search')?.addEventListener('input', renderBillsList);

// View Bill Details dynamically injected modal
const billModalHTML = `
<div id="bill-details-modal" class="modal hidden" style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 2000; display: flex; align-items: center; justify-content: center;">
    <div style="background: white; width: 90%; max-width: 500px; border-radius: 12px; padding: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); max-height: 90vh; overflow-y: auto;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; border-bottom: 1px solid var(--border-color); padding-bottom: 10px;">
            <h3 style="font-size: 18px;">Bill Details</h3>
            <button class="icon-btn" onclick="document.getElementById('bill-details-modal').classList.add('hidden')" style="color: var(--text-muted);"><i class="fas fa-times"></i></button>
        </div>
        <div id="bill-details-content" style="font-size: 14px; line-height: 1.5;"></div>
    </div>
</div>
`;
document.body.insertAdjacentHTML('beforeend', billModalHTML);

window.viewBillDetails = function(id) {
    const b = adminBills.find(x => x.id === id);
    if(!b) return;
    
    let itemsHTML = '';
    if(b.items && Array.isArray(b.items)) {
        b.items.forEach(item => {
            itemsHTML += `<div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                <span>${item.qty}x ${item.name}</span>
                <span>₹${parseFloat(item.price * item.qty).toFixed(2)}</span>
            </div>`;
        });
    }
    
    document.getElementById('bill-details-content').innerHTML = `
        <p><strong>Bill No:</strong> ${b.bill_no || b.id}</p>
        <p><strong>Date:</strong> ${b.dt ? new Date(b.dt).toLocaleString() : ''}</p>
        <p><strong>Customer:</strong> ${b.customer_name || 'Walk-in'} ${b.phone ? '('+b.phone+')' : ''}</p>
        <p><strong>Payment Method:</strong> ${b.payment_method || 'Cash'}</p>
        <hr style="border: none; border-top: 1px solid var(--border-color); margin: 15px 0;">
        <div style="background: #f8f9fa; padding: 10px; border-radius: 8px; margin-bottom: 15px;">
            <h4 style="margin-bottom: 10px; font-size: 13px; color: var(--text-muted); text-transform: uppercase;">Items</h4>
            ${itemsHTML}
        </div>
        <div style="text-align: right; font-size: 16px;">
            <p>Subtotal: ₹${parseFloat(b.subtotal || 0).toFixed(2)}</p>
            <p>Discount: ₹${parseFloat(b.discount || 0).toFixed(2)}</p>
            <p>Tax: ₹${parseFloat(b.tax || 0).toFixed(2)}</p>
            <h3 style="margin-top: 10px; color: var(--primary-color);">Total: ₹${parseFloat(b.total_amount || 0).toFixed(2)}</h3>
    <button onclick=\"if(window.printWebReceipt) window.printWebReceipt(adminBills.find(x => x.id === '" + b.id + "'))\" style=\"margin-top: 15px; padding: 10px 20px; border: none; background: #28a745; color: white; border-radius: 6px; cursor: pointer;\"><i class=\"fas fa-print\"></i> Print Receipt</button>\n        </div>
    `;
    
    document.getElementById('bill-details-modal').classList.remove('hidden');
};

// --- CUSTOMERS (CRM) MANAGEMENT ---
let adminCustomers = [];
function loadCustomers() {
    db.collection('customers').orderBy('last_order_dt', 'desc').limit(200).onSnapshot(snap => {
        adminCustomers = [];
        snap.forEach(doc => {
            adminCustomers.push({id: doc.id, ...doc.data()});
        });
        renderCustomersList();
    });
}

function renderCustomersList() {
    const list = document.getElementById('customers-list');
    if(!list) return;
    list.innerHTML = '';
    const search = (document.getElementById('customer-search').value || '').toLowerCase();
    
    adminCustomers.filter(c => (c.name || '').toLowerCase().includes(search) || (c.phone || '').includes(search)).forEach(c => {
        const tr = document.createElement('tr');
        const dt = c.last_order_dt ? new Date(c.last_order_dt).toLocaleDateString() : 'N/A';
        tr.innerHTML = `
            <td style="font-weight: 600;">${c.name || 'Unknown'}</td>
            <td>${c.phone || c.id}</td>
            <td style="text-align: center;"><span style="background: #e9ecef; padding: 4px 8px; border-radius: 12px; font-size: 12px; font-weight: bold;">${c.total_orders || 0}</span></td>
            <td style="font-size: 13px; color: var(--text-muted);">${dt}</td>
            <td style="text-align: right; font-weight: 700; color: #28a745;">₹${parseFloat(c.lifetime_value || 0).toFixed(2)}</td>
        `;
        list.appendChild(tr);
    });
}

document.getElementById('customer-search')?.addEventListener('input', renderCustomersList);

// Update switchTab hook to include bills and customers
let originalSwitchTab3 = switchTab;
switchTab = function(viewId, title) {
    if(originalSwitchTab3) originalSwitchTab3(viewId, title);
    if(viewId === 'view-bills') {
        loadBills();
    } else if(viewId === 'view-customers') {
        loadCustomers();
    }
};

// --- REPORTS & ANALYTICS ---
let salesChartInstance = null;
let itemsChartInstance = null;

function loadReports() {
    db.collection('bills').orderBy('dt', 'desc').limit(500).get().then(snap => {
        let totalSales = 0;
        let totalOrders = 0;
        let itemsCount = {};
        let dailySales = {};
        
        // Initialize last 7 days for daily sales
        for(let i=6; i>=0; i--) {
            const d = new Date();
            d.setDate(d.getDate() - i);
            const dateStr = d.toLocaleDateString();
            dailySales[dateStr] = 0;
        }

        snap.forEach(doc => {
            const b = doc.data();
            totalOrders++;
            totalSales += parseFloat(b.total_amount || 0);
            
            if(b.dt) {
                const bDateStr = new Date(b.dt).toLocaleDateString();
                if(dailySales[bDateStr] !== undefined) {
                    dailySales[bDateStr] += parseFloat(b.total_amount || 0);
                }
            }
            
            if(b.items && Array.isArray(b.items)) {
                b.items.forEach(item => {
                    const itemName = item.name || 'Unknown';
                    if(!itemsCount[itemName]) itemsCount[itemName] = 0;
                    itemsCount[itemName] += parseInt(item.qty || 1);
                });
            }
        });
        
        document.getElementById('report-total-sales').textContent = '₹' + totalSales.toFixed(2);
        document.getElementById('report-total-orders').textContent = totalOrders;
        document.getElementById('report-aov').textContent = '₹' + (totalOrders > 0 ? (totalSales/totalOrders).toFixed(2) : '0.00');
        
        renderCharts(dailySales, itemsCount);
    });
}

function renderCharts(dailySales, itemsCount) {
    const salesCtx = document.getElementById('salesChart');
    const itemsCtx = document.getElementById('itemsChart');
    if(!salesCtx || !itemsCtx) return;
    
    if(salesChartInstance) salesChartInstance.destroy();
    if(itemsChartInstance) itemsChartInstance.destroy();
    
    const labels = Object.keys(dailySales);
    const data = Object.values(dailySales);
    
    salesChartInstance = new Chart(salesCtx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Revenue (₹)',
                data: data,
                borderColor: '#007bff',
                backgroundColor: 'rgba(0,123,255,0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
    
    // Sort items by count and take top 5
    const sortedItems = Object.entries(itemsCount).sort((a,b) => b[1] - a[1]).slice(0, 5);
    
    itemsChartInstance = new Chart(itemsCtx, {
        type: 'doughnut',
        data: {
            labels: sortedItems.map(x => x[0]),
            datasets: [{
                data: sortedItems.map(x => x[1]),
                backgroundColor: ['#007bff', '#28a745', '#ffc107', '#dc3545', '#17a2b8']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

// Update switchTab hook to include reports
let originalSwitchTab4 = switchTab;
switchTab = function(viewId, title) {
    if(originalSwitchTab4) originalSwitchTab4(viewId, title);
    if(viewId === 'view-reports') {
        loadReports();
    }
};

// --- WEB SERIAL USB ESC/POS PRINTER ---
let usbPrinterPort = null;
let usbPrinterWriter = null;

document.getElementById('printer-setup-btn')?.addEventListener('click', () => {
    document.getElementById('printer-modal').classList.remove('hidden');
});

document.getElementById('connect-printer-btn')?.addEventListener('click', async () => {
    try {
        if (!navigator.serial) {
            showToast("Web Serial API not supported in this browser. Please use Chrome or Edge.", "error");
            return;
        }
        usbPrinterPort = await navigator.serial.requestPort();
        await usbPrinterPort.open({ baudRate: 9600 });
        usbPrinterWriter = usbPrinterPort.writable.getWriter();
        
        document.getElementById('connect-printer-btn').style.display = 'none';
        document.getElementById('printer-status-text').style.display = 'block';
        document.getElementById('printer-setup-btn').textContent = 'Printer Connected';
        document.getElementById('printer-setup-btn').style.background = '#28a745';
        
        const testBtn = document.getElementById('test-printer-btn');
        if (testBtn) testBtn.style.display = 'inline-block';
        
        showToast("Printer connected successfully!", "success");
        
    } catch (err) {
        console.error("Printer connection failed:", err);
        showToast("Failed to connect printer.", "error");
    }
});

function textToBytes(text) {
    return Array.from(new TextEncoder().encode(text));
}

async function printRawBytes(bytesArray) {
    if (!usbPrinterWriter) return false;
    try {
        const data = new Uint8Array(bytesArray);
        await usbPrinterWriter.write(data);
        return true;
    } catch (e) {
        console.error("Print Error:", e);
        showToast("Printer disconnected or error.", "error");
        return false;
    }
}

function padRight(str, length) {
    if(str.length > length) return str.substring(0, length);
    return str + ' '.repeat(length - str.length);
}

function padLeft(str, length) {
    if(str.length > length) return str.substring(0, length);
    return ' '.repeat(length - str.length) + str;
}

window.printWebReceipt = async function(billData) {
    if (!usbPrinterWriter) {
        // Fallback to web dialog if USB printer not connected
        return false;
    }
    
    try {
        let bytes = [];
        bytes.push(0x1B, 0x40); // Init
        bytes.push(0x1B, 0x61, 0x01); // Center align
        bytes.push(0x1D, 0x21, 0x11); // Double size
        bytes.push(...textToBytes((globalSettings.store_name || "TIWARI'S FRIED CHICKEN").toUpperCase() + "\n"));
        
        bytes.push(0x1D, 0x21, 0x00); // Normal size
        
        // Multi-line address support
        const addressLines = (globalSettings.store_address || "123 Street Name, City").split('\n');
        addressLines.forEach(line => {
            if(line.trim()) bytes.push(...textToBytes(line.trim() + "\n"));
        });
        
        if (globalSettings.store_phone) {
            bytes.push(...textToBytes("Phone: " + globalSettings.store_phone + "\n"));
        }
        bytes.push(...textToBytes("--------------------------------\n"));
        
        bytes.push(0x1B, 0x61, 0x00); // Left align
        bytes.push(...textToBytes(`Bill No: ${billData.bill_no}\n`));
        bytes.push(...textToBytes(`Date: ${new Date().toLocaleString()}\n`));
        if (billData.customer_name) bytes.push(...textToBytes(`Customer: ${billData.customer_name}\n`));
        if (billData.phone) bytes.push(...textToBytes(`Phone: ${billData.phone}\n`));
        
        bytes.push(...textToBytes("--------------------------------\n"));
        bytes.push(...textToBytes(padRight("Item", 16) + padRight("Qty", 6) + padLeft("Total", 10) + "\n"));
        bytes.push(...textToBytes("--------------------------------\n"));
        
        billData.items.forEach(item => {
            let name = padRight(item.name.substring(0, 15), 16);
            let qty = padRight(item.qty.toString(), 6);
            let total = padLeft((item.price * item.qty).toFixed(2), 10);
            bytes.push(...textToBytes(name + qty + total + "\n"));
        });
        
        bytes.push(...textToBytes("--------------------------------\n"));
        
        bytes.push(0x1B, 0x61, 0x02); // Right align
        bytes.push(...textToBytes(`Subtotal: Rs. ${parseFloat(billData.subtotal).toFixed(2)}\n`));
        if (billData.discount > 0) bytes.push(...textToBytes(`Discount: Rs. ${parseFloat(billData.discount).toFixed(2)}\n`));
        if (billData.tax > 0) bytes.push(...textToBytes(`Tax: Rs. ${parseFloat(billData.tax).toFixed(2)}\n`));
        
        bytes.push(0x1D, 0x21, 0x11); // Double size
        bytes.push(...textToBytes(`Total: Rs. ${parseFloat(billData.total || billData.total_amount || 0).toFixed(2)}\n`));
        bytes.push(0x1D, 0x21, 0x00); // Normal size
        
        bytes.push(0x1B, 0x61, 0x01); // Center align
        bytes.push(...textToBytes("\n" + (globalSettings.receipt_footer || "Thank You for visiting!") + "\n\n\n\n"));
        
        bytes.push(0x1D, 0x56, 0x41, 0x03); // Cut
        
        await printRawBytes(bytes);
        showToast("Receipt printed directly to USB!", "success");
        return true;
    } catch(e) {
        console.error(e);
        return false;
    }
};

window.printWebKOT = async function(kotData) {
    if (!usbPrinterWriter) return false;
    
    try {
        let bytes = [];
        bytes.push(0x1B, 0x40); // Init
        bytes.push(0x1B, 0x61, 0x01); // Center align
        bytes.push(0x1D, 0x21, 0x11); // Double size
        bytes.push(...textToBytes(`*** KOT - ${kotData.order_type || 'DINE-IN'} ***\n\n`));
        
        bytes.push(0x1D, 0x21, 0x00); // Normal size
        bytes.push(0x1B, 0x61, 0x00); // Left align
        bytes.push(...textToBytes(`KOT No: ${kotData.kot_no}\n`));
        bytes.push(...textToBytes(`Date: ${new Date().toLocaleString()}\n`));
        bytes.push(...textToBytes("--------------------------------\n"));
        bytes.push(...textToBytes(padRight("Item", 26) + padLeft("Qty", 6) + "\n"));
        bytes.push(...textToBytes("--------------------------------\n"));
        
        bytes.push(0x1D, 0x21, 0x10); // Double Height for visibility
        kotData.items.forEach(item => {
            let name = padRight(item.name.substring(0, 25), 26);
            let qty = padLeft(item.qty.toString(), 6);
            bytes.push(...textToBytes(name + qty + "\n"));
        });
        bytes.push(0x1D, 0x21, 0x00); // Normal size
        
        bytes.push(...textToBytes("--------------------------------\n\n\n\n"));
        bytes.push(0x1D, 0x56, 0x41, 0x03); // Cut
        
        await printRawBytes(bytes);
        return true;
    } catch(e) {
        console.error(e);
        return false;
    }
};

// --- KITCHEN DISPLAY SYSTEM (KDS) LOGIC ---
let kdsUnsubscribe = null;
let kdsData = [];

function setupKDS() {
    if (kdsUnsubscribe) kdsUnsubscribe();
    
    kdsUnsubscribe = db.collection('kots')
        .where('status', 'in', ['pending', 'preparing'])
        .onSnapshot(snapshot => {
            kdsData = [];
            snapshot.forEach(doc => {
                kdsData.push({ id: doc.id, ...doc.data() });
            });
            
            // Sort by time
            kdsData.sort((a, b) => new Date(a.dt) - new Date(b.dt));
            
            renderKDS();
        }, err => {
            console.error("KDS sync error:", err);
        });
}

function renderKDS() {
    const grid = document.getElementById('kds-grid');
    const pendingCount = document.getElementById('kds-pending-count');
    if(!grid || !pendingCount) return;
    
    grid.innerHTML = '';
    pendingCount.innerText = `${kdsData.length} Pending`;
    
    if (kdsData.length === 0) {
        grid.innerHTML = `<div style="grid-column: 1 / -1; text-align: center; color: var(--text-muted); padding: 50px;">
            <i class="fas fa-check-circle" style="font-size: 40px; margin-bottom: 15px; color: #28a745;"></i>
            <h3>All Caught Up!</h3>
            <p>No active kitchen orders at the moment.</p>
        </div>`;
        return;
    }
    
    kdsData.forEach(kot => {
        let itemsHtml = '';
        kot.items.forEach(item => {
            itemsHtml += `
                <div style="display: flex; justify-content: space-between; border-bottom: 1px dashed rgba(255,255,255,0.2); padding: 8px 0; font-size: 16px;">
                    <span style="font-weight: 500;">${item.qty}x ${item.name}</span>
                </div>
            `;
        });
        
        // Calculate time elapsed
        const orderTime = new Date(kot.dt);
        const elapsedMinutes = Math.floor((new Date() - orderTime) / 60000);
        let timeColor = elapsedMinutes > 15 ? '#ff4757' : (elapsedMinutes > 10 ? '#ffa502' : '#2ed573');
        
        let actionBtn = '';
        if (kot.status === 'pending') {
            actionBtn = `<button onclick="updateKOTStatus('${kot.id}', 'preparing')" style="width:100%; padding: 12px; background: #ffa502; color: #fff; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; font-size: 16px;">START PREPARING</button>`;
        } else if (kot.status === 'preparing') {
            actionBtn = `<button onclick="updateKOTStatus('${kot.id}', 'ready')" style="width:100%; padding: 12px; background: #2ed573; color: #fff; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; font-size: 16px;">MARK READY</button>`;
        }
        
        const card = document.createElement('div');
        card.style = `background: #2f3542; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.3); border-top: 5px solid ${kot.status === 'pending' ? '#ff4757' : '#ffa502'};`;
        card.innerHTML = `
            <div style="padding: 15px; background: rgba(0,0,0,0.2); display: flex; justify-content: space-between; align-items: center;">
                <h3 style="margin:0; color:#fff;">${kot.kot_no}</h3>
                <span style="background: rgba(0,0,0,0.5); padding: 5px 10px; border-radius: 20px; font-size: 13px; font-weight: bold; color: ${timeColor};"><i class="far fa-clock"></i> ${elapsedMinutes}m ago</span>
            </div>
            <div style="padding: 15px;">
                <div style="margin-bottom: 20px;">
                    ${itemsHtml}
                </div>
                ${actionBtn}
            </div>
        `;
        
        grid.appendChild(card);
    });
}

window.updateKOTStatus = function(id, newStatus) {
    db.collection('kots').doc(id).update({ status: newStatus }).then(() => {
        showToast("Ticket updated!", "success");
    }).catch(err => {
        console.error(err);
        showToast("Error updating ticket", "error");
    });
}

// Call setupKDS on boot
setupKDS();

// --- PHASE 6: STAFF MANAGEMENT & GLOBAL SETTINGS ---

// Secondary App for creating users without logging out
let secondaryApp = null;
try {
    secondaryApp = firebase.initializeApp(firebaseConfig, "Secondary");
} catch(e) { console.log(e); }

// STAFF MANAGEMENT LOGIC
let staffUnsubscribe = null;
function setupStaffManagement() {
    if (currentUserRole !== 'super_admin' && currentUserRole !== 'manager') return;
    
    if (staffUnsubscribe) staffUnsubscribe();
    staffUnsubscribe = db.collection('users').onSnapshot(snap => {
        const tbody = document.getElementById('staff-table-body');
        if (!tbody) return;
        
        tbody.innerHTML = '';
        snap.forEach(doc => {
            const data = doc.data();
            let roleBadge = '';
            if (data.role === 'super_admin') roleBadge = '<span style="background: #e1b12c; color: #fff; padding: 4px 8px; border-radius: 6px; font-size: 12px; font-weight: bold;">Super Admin</span>';
            else if (data.role === 'manager') roleBadge = '<span style="background: #3498db; color: #fff; padding: 4px 8px; border-radius: 6px; font-size: 12px;">Manager</span>';
            else if (data.role === 'kitchen') roleBadge = '<span style="background: #e74c3c; color: #fff; padding: 4px 8px; border-radius: 6px; font-size: 12px;">Kitchen</span>';
            else roleBadge = '<span style="background: #2ecc71; color: #fff; padding: 4px 8px; border-radius: 6px; font-size: 12px;">Cashier</span>';
            
            const status = data.is_active === false ? '<span style="color: #e74c3c;">Inactive</span>' : '<span style="color: #2ecc71;">Active</span>';
            
            tbody.innerHTML += `
                <tr style="border-bottom: 1px solid var(--border-color);">
                    <td style="padding: 15px; font-weight: bold;">${data.display_name || 'N/A'}</td>
                    <td>${data.email}</td>
                    <td>${roleBadge}</td>
                    <td>${status}</td>
                    <td style="text-align: right; padding-right: 15px;">
                        <button onclick="toggleStaffStatus('${doc.id}', ${data.is_active !== false})" class="icon-btn" style="color: ${data.is_active !== false ? '#e74c3c' : '#2ecc71'};" title="${data.is_active !== false ? 'Deactivate' : 'Activate'}"><i class="fas fa-power-off"></i></button>
                    </td>
                </tr>
            `;
        });
    });
}

document.getElementById('btn-save-staff')?.addEventListener('click', async () => {
    const name = document.getElementById('staff-name').value;
    const email = document.getElementById('staff-email').value;
    const pwd = document.getElementById('staff-pwd').value;
    const role = document.getElementById('staff-role').value;
    
    if (!name || !email || !pwd) return showToast("Fill all fields", "error");
    if (pwd.length < 6) return showToast("Password must be 6+ chars", "error");
    
    const btn = document.getElementById('btn-save-staff');
    const originalBtn = btn.innerHTML;
    btn.innerHTML = "Creating...";
    
    try {
        // Create Auth Account in secondary app
        const res = await secondaryApp.auth().createUserWithEmailAndPassword(email, pwd);
        
        // Save to Firestore
        await db.collection('users').doc(res.user.uid).set({
            display_name: name,
            email: email,
            role: role,
            is_active: true,
            created_at: new Date().toISOString()
        });
        
        // Sign out secondary so it can be reused
        await secondaryApp.auth().signOut();
        
        showToast("Staff account created successfully!");
        document.getElementById('staff-modal').classList.add('hidden');
        document.getElementById('staff-name').value = '';
        document.getElementById('staff-email').value = '';
        document.getElementById('staff-pwd').value = '';
        
    } catch(err) {
        console.error(err);
        showToast("Error: " + err.message, "error");
    } finally {
        btn.innerHTML = originalBtn;
    }
});

window.toggleStaffStatus = function(uid, currentlyActive) {
    if(confirm(`Are you sure you want to ${currentlyActive ? 'deactivate' : 'activate'} this staff member?`)) {
        db.collection('users').doc(uid).update({ is_active: !currentlyActive }).then(() => {
            showToast("Staff status updated!");
        });
    }
};

// GLOBAL SETTINGS LOGIC
let globalSettings = {
    store_name: "Tiwari's Fried Chicken",
    store_phone: "+91 9999999999",
    store_address: "123 Street Name, City",
    tax_rate: 0,
    receipt_footer: "Thank You for visiting!"
};

function loadGlobalSettings() {
    db.collection('settings').doc('global').onSnapshot(doc => {
        if (doc.exists) {
            globalSettings = { ...globalSettings, ...doc.data() };
            // Populate UI if Settings tab is open
            const nameEl = document.getElementById('setting-store-name');
            if(nameEl) {
                nameEl.value = globalSettings.store_name || '';
                document.getElementById('setting-store-phone').value = globalSettings.store_phone || '';
                document.getElementById('setting-store-address').value = globalSettings.store_address || '';
                document.getElementById('setting-tax-rate').value = globalSettings.tax_rate || 0;
                document.getElementById('setting-receipt-footer').value = globalSettings.receipt_footer || '';
            }
        }
    });
}

document.getElementById('btn-save-settings')?.addEventListener('click', () => {
    const data = {
        store_name: document.getElementById('setting-store-name').value,
        store_phone: document.getElementById('setting-store-phone').value,
        store_address: document.getElementById('setting-store-address').value,
        tax_rate: parseFloat(document.getElementById('setting-tax-rate').value) || 0,
        receipt_footer: document.getElementById('setting-receipt-footer').value
    };
    
    db.collection('settings').doc('global').set(data, {merge: true}).then(() => {
        showToast("Global settings saved successfully!");
    }).catch(err => {
        showToast("Error saving settings", "error");
        console.error(err);
    });
});

// Load immediately
loadGlobalSettings();
// Load staff when possible
setTimeout(setupStaffManagement, 2000);

// --- MENU CATALOG MANAGER ---
window.editProduct = function(id) {
    const p = posProducts.find(x => x.id === id);
    if (!p) return;
    
    document.getElementById('prod-name-input').value = p.name || '';
    document.getElementById('prod-cat-input').value = p.category || '';
    document.getElementById('prod-price-offline-input').value = p.price_offline || p.price || '';
    document.getElementById('prod-price-online-input').value = p.price_online || p.price_offline || p.price || '';
    document.getElementById('prod-web-available').checked = p.web_available !== false;
    document.getElementById('prod-image-url').value = p.image_path || '';
    
    const preview = document.getElementById('prod-image-preview');
    const icon = document.getElementById('prod-image-icon');
    if (p.image_path) {
        preview.src = p.image_path;
        preview.style.display = 'block';
        icon.style.display = 'none';
    } else {
        preview.src = '';
        preview.style.display = 'none';
        icon.style.display = 'block';
    }
    
    document.getElementById('save-product-btn').onclick = () => saveProduct(id);
    document.getElementById('product-modal').classList.remove('hidden');
}

document.getElementById('add-product-btn')?.addEventListener('click', () => {
    document.getElementById('prod-name-input').value = '';
    document.getElementById('prod-cat-input').value = '';
    document.getElementById('prod-price-offline-input').value = '';
    document.getElementById('prod-price-online-input').value = '';
    document.getElementById('prod-web-available').checked = true;
    document.getElementById('prod-image-url').value = '';
    document.getElementById('prod-image-preview').style.display = 'none';
    document.getElementById('prod-image-icon').style.display = 'block';
    document.getElementById('prod-image-input').value = '';
    
    document.getElementById('save-product-btn').onclick = () => saveProduct(null);
    document.getElementById('product-modal').classList.remove('hidden');
});

// Firebase Storage Image Upload
document.getElementById('prod-image-input')?.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    const progress = document.getElementById('prod-upload-progress');
    progress.style.display = 'block';
    
    const storageRef = storage.ref('products/' + Date.now() + '_' + file.name);
    const task = storageRef.put(file);
    
    task.on('state_changed', 
        (snapshot) => {
            const pct = (snapshot.bytesTransferred / snapshot.totalBytes) * 100;
            progress.innerText = `Uploading: ${Math.round(pct)}%`;
        }, 
        (error) => {
            console.error(error);
            showToast("Image upload failed", "error");
            progress.style.display = 'none';
        }, 
        async () => {
            const url = await task.snapshot.ref.getDownloadURL();
            document.getElementById('prod-image-url').value = url;
            document.getElementById('prod-image-preview').src = url;
            document.getElementById('prod-image-preview').style.display = 'block';
            document.getElementById('prod-image-icon').style.display = 'none';
            progress.innerText = 'Upload Complete!';
            setTimeout(() => progress.style.display = 'none', 2000);
        }
    );
});

async function saveProduct(id) {
    const name = document.getElementById('prod-name-input').value;
    const cat = document.getElementById('prod-cat-input').value;
    const priceOffline = parseFloat(document.getElementById('prod-price-offline-input').value || 0);
    const priceOnline = parseFloat(document.getElementById('prod-price-online-input').value || priceOffline);
    const webAvail = document.getElementById('prod-web-available').checked;
    const imgUrl = document.getElementById('prod-image-url').value;
    
    if (!name || priceOffline <= 0) {
        showToast("Name and Dine-In Price are required!", "error");
        return;
    }
    
    const btn = document.getElementById('save-product-btn');
    const oldText = btn.innerHTML;
    btn.innerHTML = "Saving...";
    
    const data = {
        name: name,
        category: cat,
        price_offline: priceOffline,
        price_online: priceOnline,
        price: priceOffline, // Fallback for POS if it uses .price directly
        web_available: webAvail,
        image_path: imgUrl,
        is_active: webAvail
    };
    
    try {
        if (id) {
            await db.collection('products').doc(id).update(data);
            showToast("Product Updated!");
        } else {
            await db.collection('products').add(data);
            showToast("Product Added!");
        }
        document.getElementById('product-modal').classList.add('hidden');
    } catch(err) {
        console.error(err);
        showToast("Error saving product", "error");
    } finally {
        btn.innerHTML = oldText;
    }
}

// --- PHASE 8: CRM, COMBOS & EMAIL ---

// Combo UI Toggle
document.getElementById('prod-is-combo')?.addEventListener('change', (e) => {
    const container = document.getElementById('combo-items-container');
    if(e.target.checked) {
        container.classList.remove('hidden');
        populateComboSelect();
    } else {
        container.classList.add('hidden');
    }
});

function populateComboSelect() {
    const select = document.getElementById('combo-product-select');
    if(!select) return;
    select.innerHTML = '';
    posProducts.filter(p => p.is_combo !== true).forEach(p => {
        select.innerHTML += `<option value="${p.id}">${p.name} (,1${p.price_offline || p.price || 0})</option>`;
    });
}

let currentComboItems = [];
document.getElementById('btn-add-combo-item')?.addEventListener('click', () => {
    const select = document.getElementById('combo-product-select');
    const qty = parseInt(document.getElementById('combo-qty-input').value) || 1;
    if(!select.value) return;
    
    const p = posProducts.find(x => x.id === select.value);
    if(p) {
        currentComboItems.push({ id: p.id, name: p.name, qty: qty });
        renderComboItems();
    }
});

function renderComboItems() {
    const list = document.getElementById('combo-items-list');
    if(!list) return;
    list.innerHTML = '';
    currentComboItems.forEach((c, idx) => {
        list.innerHTML += `<li style="margin-bottom: 5px; display: flex; justify-content: space-between;">
            <span>${c.qty}x ${c.name}</span>
            <button onclick="currentComboItems.splice(${idx}, 1); renderComboItems();" style="background:none; border:none; color:red; cursor:pointer;"><i class="fas fa-times"></i></button>
        </li>`;
    });
    document.getElementById('combo-items-data').value = JSON.stringify(currentComboItems);
}

// Intercept window.editProduct to load combo items
const originalEditProductPhase8 = window.editProduct;
window.editProduct = function(id) {
    if(originalEditProductPhase8) originalEditProductPhase8(id);
    
    const p = posProducts.find(x => x.id === id);
    if(!p) return;
    
    const isCombo = p.is_combo === true;
    document.getElementById('prod-is-combo').checked = isCombo;
    if(isCombo) {
        document.getElementById('combo-items-container').classList.remove('hidden');
        currentComboItems = p.combo_items ? (typeof p.combo_items === 'string' ? JSON.parse(p.combo_items) : p.combo_items) : [];
        populateComboSelect();
        renderComboItems();
    } else {
        document.getElementById('combo-items-container').classList.add('hidden');
        currentComboItems = [];
        renderComboItems();
    }
};

// Hook into saveProduct using JS proxy / override
const originalSaveProductPhase8 = window.saveProduct;
window.saveProduct = async function(id) {
    const name = document.getElementById('prod-name-input').value;
    const cat = document.getElementById('prod-cat-input').value;
    const priceOffline = parseFloat(document.getElementById('prod-price-offline-input').value || 0);
    const priceOnline = parseFloat(document.getElementById('prod-price-online-input').value || priceOffline);
    const webAvail = document.getElementById('prod-web-available').checked;
    const imgUrl = document.getElementById('prod-image-url').value;
    
    const isCombo = document.getElementById('prod-is-combo').checked;
    const comboItems = JSON.parse(document.getElementById('combo-items-data').value || '[]');
    
    if (!name || priceOffline <= 0) {
        showToast("Name and Dine-In Price are required!", "error");
        return;
    }
    
    const btn = document.getElementById('save-product-btn');
    const oldText = btn.innerHTML;
    btn.innerHTML = "Saving...";
    
    const data = {
        name: name,
        category: cat,
        price_offline: priceOffline,
        price_online: priceOnline,
        price: priceOffline, 
        web_available: webAvail,
        image_path: imgUrl,
        is_active: webAvail,
        is_combo: isCombo,
        combo_items: comboItems
    };
    
    try {
        if (id) {
            await db.collection('products').doc(id).update(data);
            showToast("Product Updated!");
        } else {
            await db.collection('products').add(data);
            showToast("Product Added!");
        }
        document.getElementById('product-modal').classList.add('hidden');
    } catch(err) {
        console.error(err);
        showToast("Error saving product", "error");
    } finally {
        btn.innerHTML = oldText;
    }
};

// Email Receipt logic
document.getElementById('btn-email-receipt')?.addEventListener('click', () => {
    const email = document.getElementById('pos-customer-email').value;
    if(!email) return showToast("Enter an email address", "error");
    
    let subtotal = 0;
    posCart.forEach(i => subtotal += i.price * i.qty);
    const discount = parseFloat(document.getElementById('pos-discount').value || 0);
    const taxRate = typeof globalSettings !== 'undefined' && globalSettings.tax_rate ? parseFloat(globalSettings.tax_rate) : 5;
    const tax = (subtotal - discount) * (taxRate / 100);
    const total = subtotal - discount + tax;
    
    let text = `Thank you for dining at ${(globalSettings && globalSettings.store_name) ? globalSettings.store_name : "Tiwari's Fried Chicken"}!\n\n`;
    text += `Your Order:\n`;
    posCart.forEach(i => {
        text += `- ${i.qty}x ${i.name} (,1${i.price * i.qty})\n`;
    });
    text += `\nSubtotal: ,1${subtotal.toFixed(2)}`;
    if(discount > 0) text += `\nDiscount: -,1${discount.toFixed(2)}`;
    text += `\nTax (${taxRate}%): ,1${tax.toFixed(2)}`;
    text += `\nTotal: ,1${total.toFixed(2)}\n\n`;
    text += (globalSettings && globalSettings.receipt_footer) ? globalSettings.receipt_footer : "Thank You for visiting!";
    
    const mailto = `mailto:${encodeURIComponent(email)}?subject=${encodeURIComponent("Your Receipt from " + (globalSettings && globalSettings.store_name ? globalSettings.store_name : "TFC"))}&body=${encodeURIComponent(text)}`;
    window.location.href = mailto;
    showToast("Email client opened!");
});

// Override renderCustomers for Phase 8
window.renderCustomers = function() {
    const list = document.getElementById('customers-list');
    if (!list) return;
    list.innerHTML = '';
    const search = (document.getElementById('customer-search').value || '').toLowerCase();
    
    customersData.filter(c => 
        (c.name || '').toLowerCase().includes(search) || 
        (c.phone || '').toLowerCase().includes(search)
    ).forEach(c => {
        const tr = document.createElement('tr');
        
        let statusBadge = '<span style="background: #e9ecef; padding: 4px 8px; border-radius: 6px; font-size: 11px;">New</span>';
        if (c.visits >= 5) statusBadge = '<span style="background: #f1c40f; color: #fff; padding: 4px 8px; border-radius: 6px; font-size: 11px; font-weight: bold;">🌟 Loyal</span>';
        else if (c.visits >= 2) statusBadge = '<span style="background: #3498db; color: #fff; padding: 4px 8px; border-radius: 6px; font-size: 11px;">Active</span>';
        
        if (c.lastVisit && (new Date() - new Date(c.lastVisit)) > 30*24*60*60*1000) {
            statusBadge = '<span style="background: #e74c3c; color: #fff; padding: 4px 8px; border-radius: 6px; font-size: 11px;">Dormant</span>';
        }
        
        let favItem = 'N/A';
        if (c.items && Object.keys(c.items).length > 0) {
            favItem = Object.entries(c.items).sort((a,b) => b[1] - a[1])[0][0];
        }

        tr.innerHTML = `
            <td style="font-weight: 600;">${c.name || 'Unknown'}</td>
            <td>${c.phone}</td>
            <td>${statusBadge}</td>
            <td>${c.visits} orders</td>
            <td><span style="background: #ffeaa7; color: #d35400; padding: 4px 8px; border-radius: 6px; font-size: 11px;"><i class="fas fa-star"></i> ${favItem}</span></td>
            <td style="text-align: right; color: var(--primary-color); font-weight: bold;">,1${(c.totalSpent || 0).toFixed(2)}</td>
        `;
        list.appendChild(tr);
    });
};

// --- PHASE 9: POS Handoff ---
window.sendOrderToPOS = function(orderId) {
    if (!adminOrdersData[orderId]) {
        showToast("Order details not found!", "error");
        return;
    }
    const order = adminOrdersData[orderId];
    
    // Clear current POS cart
    posCart = [];
    
    // Load items into POS cart
    if (order.items && Array.isArray(order.items)) {
        order.items.forEach(item => {
            if (item.id === 'discount' || item.id === 'delivery') return; // Skip virtual items for now, or handle them via POS discount field
            posCart.push({
                id: item.id || Math.random().toString(36).substr(2, 9),
                name: item.name,
                price: parseFloat(item.price) || 0,
                qty: parseInt(item.qty) || 1
            });
        });
    }
    
    // Set Customer Info
    document.getElementById('pos-customer-phone').value = order.customer_phone || '';
    document.getElementById('pos-customer-name').value = order.customer_name || 'Web Order';
    
    // Attempt to parse discount
    let discount = 0;
    if (order.items) {
        const discountItem = order.items.find(i => i.id === 'discount');
        if (discountItem) discount = Math.abs(discountItem.price);
    }
    document.getElementById('pos-discount').value = discount > 0 ? discount : '';
    
    // Update Cart UI and switch to POS tab
    updateCartTotals();
    renderCart();
    switchView('view-pos');
    
    // Optional: Mark web order as ready/completed so it leaves the live queue
    db.collection('web_orders').doc(orderId).update({ status: 'ready' }).catch(e => console.error(e));
    
    showToast("Order loaded into POS for billing!");
};



// --- TEST PRINTER LOGIC ---
const testPrinterBtn = document.getElementById('test-printer-btn');
if (testPrinterBtn) {
    testPrinterBtn.addEventListener('click', async () => {
        if (!usbPrinterWriter) {
            showToast("Printer not connected!", "error");
            return;
        }
        try {
            const paperWidth = document.getElementById('printer-paper-width').value;
            const widthChars = paperWidth === '80' ? 48 : 32;
            
            let receiptText = "TFC POS SYSTEM\n";
            receiptText += "================================\n";
            receiptText += "Connection: Serial (COM)\n";
            receiptText += `Paper Width: ${paperWidth}mm (${widthChars} chars)\n`;
            receiptText += "Status: SUCCESS\n";
            receiptText += "================================\n";
            receiptText += "Thank you for using TFC POS!\n\n\n\n";
            
            await printRawBytes([
                0x1B, 0x40, // Init
                0x1B, 0x61, 0x01, // Center
                0x1D, 0x21, 0x11, // Double height & width
                0x1B, 0x45, 0x01, // Bold ON
                ...textToBytes("PRINTER TEST\n"),
                0x1D, 0x21, 0x00, // Normal size
                0x1B, 0x45, 0x00, // Bold OFF
                0x1B, 0x61, 0x00, // Left align
                ...textToBytes(receiptText),
                0x1D, 0x56, 0x41, 0x03 // Cut
            ]);
            
            showToast("Test print sent!");
        } catch (e) {
            console.error("Print Error:", e);
            showToast("Print failed: " + e.message, "error");
        }
    });
}
