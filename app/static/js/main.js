(function(){
	console.log('Comp360Flow JS loaded');
	// Modal focus trap and open/close handlers
	function trapFocus(container){
		if (!container) return;
		const selectors = 'a, button, input, select, textarea, [tabindex]:not([tabindex="-1"])';
		const focusable = container.querySelectorAll(selectors);
		if (!focusable.length) return;
		const first = focusable[0];
		const last = focusable[focusable.length - 1];
		container.addEventListener('keydown', (e)=>{
			if (e.key !== 'Tab') return;
			if (e.shiftKey && document.activeElement === first){ last.focus(); e.preventDefault(); }
			else if (!e.shiftKey && document.activeElement === last){ first.focus(); e.preventDefault(); }
		});
	}
	document.querySelectorAll('[data-modal-target]').forEach(btn => {
		btn.addEventListener('click', () => {
			const id = btn.getAttribute('data-modal-target');
			const modal = document.getElementById(id);
			if (!modal) return;
			modal.setAttribute('aria-hidden','false');
			const dialog = modal.querySelector('.dialog');
			if (dialog){ trapFocus(dialog); dialog.setAttribute('tabindex','-1'); dialog.focus(); }
		});
	});
	document.querySelectorAll('[data-modal-close]').forEach(btn => {
		btn.addEventListener('click', () => {
			const modal = btn.closest('.modal');
			if (modal){ modal.setAttribute('aria-hidden','true'); }
		});
	});

	// Tooltips
	document.querySelectorAll('[data-tooltip]').forEach(el => {
		el.classList.add('tooltip');
		el.setAttribute('aria-expanded','false');
		// Create tooltip content element if title attribute exists
		const title = el.getAttribute('title');
		if (title){
			el.removeAttribute('title');
			const c = document.createElement('div'); c.className='tooltip-content'; c.textContent = title; el.appendChild(c);
		}
		el.addEventListener('mouseenter', ()=> el.setAttribute('aria-expanded','true'));
		el.addEventListener('mouseleave', ()=> el.setAttribute('aria-expanded','false'));
	});

	// Toasts
	window.showToast = function(message, variant){
		const container = document.querySelector('.toast-container') || (function(){
			const c = document.createElement('div'); c.className='toast-container'; document.body.appendChild(c); return c;
		})();
		const toast = document.createElement('div');
		toast.className = 'toast';
		const root = getComputedStyle(document.documentElement);
		if (variant === 'success') toast.style.borderLeftColor = root.getPropertyValue('--success');
		if (variant === 'warning') toast.style.borderLeftColor = root.getPropertyValue('--warning');
		if (variant === 'danger') toast.style.borderLeftColor = root.getPropertyValue('--danger');
		toast.textContent = message;
		container.appendChild(toast);
		setTimeout(()=> toast.remove(), 3500);
	}

		// Controls detail dynamic load
		document.addEventListener('click', async (e) => {
			const btn = e.target.closest('.view-control');
			if (!btn) return;
			const controlId = btn.getAttribute('data-id');
			const modal = document.getElementById('control-detail');
			if (!controlId || !modal) return;
			try {
				const params = new URLSearchParams(window.location.search);
				const org = params.get('org');
				const url = `/controls/api/${controlId}${org ? `?org=${encodeURIComponent(org)}` : ''}`;
				const resp = await fetch(url, { headers: { 'Accept': 'application/json' } });
				if (!resp.ok) throw new Error('Failed to load control');
				const data = await resp.json();
				modal.querySelector('#controlTitle').textContent = `${data.control_id} • ${data.title}`;
				modal.querySelector('#controlMeta').textContent = `${data.framework || ''} • ${data.owner || 'Unassigned'} • ${data.status || 'Not Started'}`;
				const desc = modal.querySelector('#controlDescription');
				if (desc) desc.textContent = data.description || 'No description';
				// Fill tasks
				const tasks = Array.isArray(data.tasks) ? data.tasks : [];
				const tList = modal.querySelector('#controlTasks');
				if (tList) {
					tList.innerHTML = '';
					if (tasks.length === 0) {
						const li = document.createElement('li'); li.textContent = 'No recent tasks'; tList.appendChild(li);
					} else {
						tasks.forEach(t => {
							const li = document.createElement('li');
							const who = t.assignee_name ? ` • ${t.assignee_name}` : '';
							li.textContent = `${t.title} • ${t.status || 'pending'}${t.due_date ? ' • due ' + t.due_date : ''}${who}`;
							tList.appendChild(li);
						});
					}
					// Add view all link (if tasks endpoint exists)
					const existingLink = modal.querySelector('#tasksViewAll');
					if (!existingLink) {
						const a = document.createElement('a');
						a.id = 'tasksViewAll'; a.href = `/tasks${org ? `?org=${encodeURIComponent(org)}&control=${encodeURIComponent(data.id)}` : ''}`;
						a.textContent = `View all (${tasks.length})`;
						a.style.marginTop = '8px'; a.style.display = 'inline-block';
						tList.parentElement.appendChild(a);
					} else {
						existingLink.href = `/tasks${org ? `?org=${encodeURIComponent(org)}&control=${encodeURIComponent(data.id)}` : ''}`;
						existingLink.textContent = `View all (${tasks.length})`;
					}
				}
				// Fill evidence
				const ev = Array.isArray(data.evidence) ? data.evidence : [];
				const eList = modal.querySelector('#controlEvidence');
				if (eList) {
					eList.innerHTML = '';
					if (ev.length === 0) {
						const li = document.createElement('li'); li.textContent = 'No recent evidence'; eList.appendChild(li);
					} else {
						ev.forEach(f => {
							const li = document.createElement('li');
							li.textContent = `${f.file_name || 'Attachment'}${f.created_at ? ' • ' + f.created_at.substring(0,10) : ''}`;
							eList.appendChild(li);
						});
					}
					// Add view all link for evidence
					const existingEvLink = modal.querySelector('#evidenceViewAll');
					if (!existingEvLink) {
						const a = document.createElement('a');
						a.id = 'evidenceViewAll'; a.href = `/reports/evidence${org ? `?org=${encodeURIComponent(org)}&control=${encodeURIComponent(data.id)}` : ''}`;
						a.textContent = `View all (${ev.length})`;
						a.style.marginTop = '8px'; a.style.display = 'inline-block';
						eList.parentElement.appendChild(a);
					} else {
						existingEvLink.href = `/reports/evidence${org ? `?org=${encodeURIComponent(org)}&control=${encodeURIComponent(data.id)}` : ''}`;
						existingEvLink.textContent = `View all (${ev.length})`;
					}
				}
			} catch (err) {
				console.error(err);
				showToast('Could not load control details', 'danger');
			}
		});
})();
