
function generatePDFBill(billData) {
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF({
        orientation: 'portrait',
        unit: 'mm',
        format: [80, 200] // Thermal receipt size roughly 80mm width
    });

    let y = 10;
    
    // Header
    doc.setFontSize(14);
    doc.setFont('helvetica', 'bold');
    doc.text("TIWARI'S FRIED CHICKEN", 40, y, { align: 'center' });
    y += 5;
    
    doc.setFontSize(9);
    doc.setFont('helvetica', 'normal');
    doc.text("OT Road, near ITI Chhak, Balasore", 40, y, { align: 'center' });
    y += 4;
    doc.text("Phone: +91 7609825488", 40, y, { align: 'center' });
    y += 8;
    
    // Bill details
    doc.setFontSize(9);
    doc.text(`Bill No: ${billData.bill_no}`, 5, y);
    y += 5;
    const dtStr = new Date(billData.dt).toLocaleString();
    doc.text(`Date: ${dtStr}`, 5, y);
    y += 6;
    
    doc.line(5, y, 75, y);
    y += 4;
    
    // Items table
    doc.setFont('helvetica', 'bold');
    doc.text("Item", 5, y);
    doc.text("Qty", 45, y);
    doc.text("Amt", 60, y);
    y += 2;
    doc.line(5, y, 75, y);
    y += 5;
    
    doc.setFont('helvetica', 'normal');
    billData.items.forEach(item => {
        const itemName = item.name.substring(0, 20); // truncate
        doc.text(itemName, 5, y);
        doc.text(item.qty.toString(), 45, y);
        const amt = (item.price * item.qty).toFixed(2);
        doc.text(amt.toString(), 60, y);
        y += 5;
    });
    
    y += 2;
    doc.line(5, y, 75, y);
    y += 5;
    
    // Totals
    doc.text("Subtotal:", 35, y);
    doc.text(billData.subtotal.toFixed(2), 75, y, { align: 'right' });
    y += 5;
    
    if (billData.discount > 0) {
        doc.text("Discount:", 35, y);
        doc.text("-" + billData.discount.toFixed(2), 75, y, { align: 'right' });
        y += 5;
    }
    
    if (billData.tax > 0) {
        doc.text("Tax (5%):", 35, y);
        doc.text(billData.tax.toFixed(2), 75, y, { align: 'right' });
        y += 5;
    }
    
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(11);
    doc.text("Total:", 35, y);
    doc.text(billData.total_amount.toFixed(2), 75, y, { align: 'right' });
    y += 10;
    
    doc.setFontSize(9);
    doc.setFont('helvetica', 'italic');
    doc.text("Thank you for visiting us!", 40, y, { align: 'center' });
    
    // Save PDF
    doc.save(`${billData.bill_no}.pdf`);
    
    // WhatsApp Prompt
    setTimeout(() => {
        if (confirm("Bill downloaded! Do you want to share it via WhatsApp?")) {
            const text = `Hello! Here is your bill from Tiwari's Fried Chicken.\n\nBill No: ${billData.bill_no}\nAmount: ₹${billData.total_amount.toFixed(2)}\nDate: ${dtStr}\n\nThank you for dining with us!`;
            window.location.href = `whatsapp://send?text=${encodeURIComponent(text)}`;
        }
    }, 500);
}

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

// UI Elements
const toastEl = document.getElementById('toast');
  const authContainer = document.getElementById('auth-container');
  const appContainer = document.getElementById('app-container');
  const logoutBtn = document.getElementById('logout-btn');
  const loginBtn = document.getElementById('admin-login-btn');
  const pwdInput = document.getElementById('admin-pwd-input');

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
    document.getElementById(tabId).classList.remove('hidden');
    document.getElementById(tabId).classList.add('active-tab');
    
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    document.querySelector(`.nav-item[data-target="${tabId}"]`).classList.add('active');
    
    document.getElementById('header-title-text').textContent = title;
}

// --- AUTH LOGIC ---
auth.onAuthStateChanged(user => {
    if (user) {
        if (typeof loadDashboard === "function") loadDashboard();
        if (user.email === ADMIN_EMAIL) {
            showView('app-container');
            if (typeof initDashboard === "function") initDashboard();
        } else {
            auth.signOut().then(() => {
                showToast("Access Denied: You must use the official TFC Admin Gmail account.", "error");
            });
            showView('auth-container');
        }
    } else {
        showView('auth-container');
    }
});

if (loginBtn) {
    loginBtn.addEventListener('click', (e) => {
        e.preventDefault();
        const pwd = pwdInput.value;
        if (pwd === 'Tfcbls@123') {
            auth.signInWithEmailAndPassword(ADMIN_EMAIL, pwd)
                .then((result) => {
                    showToast("Login successful!");
                })
                .catch((error) => {
                    showToast("Error: " + error.message, "error");
                });
        } else {
            showToast("Incorrect Admin Password!", "error");
        }
    });
}

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
    let currentFilter = 'pending';
    
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentFilter = btn.getAttribute('data-filter');
            renderOrders();
        });
    });

    if (liveOrdersUnsubscribe) liveOrdersUnsubscribe();
    
    liveOrdersUnsubscribe = db.collection('web_orders')
        .where('status', 'in', ['pending', 'preparing'])
        .onSnapshot(snapshot => {
            window.adminOrdersData = [];
            snapshot.forEach(doc => {
                window.adminOrdersData.push({ id: doc.id, ...doc.data() });
            });
            
            // Sort by timestamp
            window.adminOrdersData.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
            
            const pendingCount = window.adminOrdersData.filter(o => o.status === 'pending').length;
            if (pendingCount > 0) {
                badge.textContent = pendingCount;
                badge.classList.remove('hidden');
            } else {
                badge.classList.add('hidden');
            }
            
            document.getElementById('metric-kots').textContent = window.adminOrdersData.length;
            renderOrders();
        });

    function renderOrders() {
        const ordersList = document.getElementById('live-orders-list');
        if (!ordersList) return;
        
        try {
            ordersList.innerHTML = '';
            const filtered = (window.adminOrdersData || []).filter(o => o.status === currentFilter);
            
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
                        <span class="card-title">${order.customer_name || 'Guest'} <br><small>${order.customer_phone || ''}</small></span>
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
                        <button class="btn-small btn-ready" onclick="finishOrder('${order.id}')">Finish & Bill</button>
                    `;
                }
            });
        } catch (err) {
            console.error(err);
            if(typeof showToast === 'function') { showToast('UI Error: ' + err.message, 'error'); }
        }
    }
}

window.finishOrder = function(orderId) {
    const order = (window.adminOrdersData || []).find(o => o.id === orderId);
    if (!order) return;
    
    db.collection('web_orders').doc(orderId).update({
        status: 'ready',
        updated_at: new Date().toISOString()
    }).then(() => {
        showToast('Order marked as ready. Loading POS...');
        
        posCart = [];
        let parsedItems = order.items || [];
        if(typeof parsedItems === 'string') { try { parsedItems = JSON.parse(parsedItems); } catch(e) { parsedItems = []; } }
        
        (Array.isArray(parsedItems) ? parsedItems : []).forEach(item => {
            posCart.push({
                name: item.name,
                price: parseFloat(item.price || 0),
                qty: parseInt(item.qty || 1)
            });
        });
        
        const dInput = document.getElementById('pos-discount');
        if(dInput) dInput.value = '';
        
        const cn = document.getElementById('bill-customer-name');
        if(cn) cn.value = order.customer_name || 'Guest';
        const cp = document.getElementById('bill-customer-phone');
        if(cp) cp.value = order.customer_phone || '';
        
        updateCartTotals();
        switchTab('view-pos', 'POS / Billing');
        
    }).catch(err => {
        showToast(err.message, 'error');
    });
};

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
            const dt = new Date(bill.dt).toLocaleString();
            card.innerHTML = `
                <div class="card-header">
                    <span class="card-title">Bill #${bill.bill_no}</span>
                    <span class="card-badge badge-ready">₹${(bill.total_amount || bill.total || 0).toFixed(2)}</span>
                </div>
                <div class="card-body">
                    <p><strong>Customer:</strong> ${bill.customer_name || 'Guest'}</p>
                    <p><strong>Date:</strong> ${dt}</p>
                </div>
                <div class="card-actions">
                    <button class="btn-small btn-accept" onclick='generatePDFBill(${JSON.stringify(bill).replace(/'/g, "\'")})'><i class="fas fa-file-pdf"></i> PDF</button>
                </div>
            `;
            billsList.appendChild(card);
        });
    }
}

function loadCustomers() {
    const list = document.getElementById('customers-list');
    db.collection('users').limit(50).onSnapshot(snapshot => {
        list.innerHTML = '';
        if (snapshot.empty) {
            list.innerHTML = '<p style="text-align:center; color:#888; padding: 20px;">No customers found.</p>';
            return;
        }
        
        snapshot.forEach(doc => {
            const u = doc.data();
            const card = document.createElement('div');
            card.className = 'list-card';
            card.innerHTML = `
                <div class="card-header">
                    <span class="card-title">${u.name || 'Unknown'}</span>
                </div>
                <div class="card-body">
                    <p><i class="fas fa-envelope"></i> ${u.email || 'N/A'}</p>
                    <p><i class="fas fa-phone"></i> ${u.phone || 'N/A'}</p>
                </div>
            `;
            list.appendChild(card);
        });
    });
}
