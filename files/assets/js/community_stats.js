(() => {
	'use strict';

	const SVG_WIDTH = 1000;
	const SVG_HEIGHT = 190;
	const PAD = 12;
	const USABLE_WIDTH = SVG_WIDTH - (PAD * 2);
	const USABLE_HEIGHT = SVG_HEIGHT - (PAD * 2);
	const numberFormat = new Intl.NumberFormat();

	function clamp(value, min, max) {
		return Math.min(Math.max(value, min), max);
	}

	function dateLabel(epochSeconds, bucketName) {
		const date = new Date(epochSeconds * 1000);
		const formatted = new Intl.DateTimeFormat(undefined, {
			day: 'numeric',
			month: 'short',
			year: 'numeric',
			timeZone: 'UTC',
		}).format(date);
		return bucketName === 'week' ? `Week of ${formatted}` : formatted;
	}

	function shortDateLabel(epochSeconds, bucketName) {
		const date = new Date(epochSeconds * 1000);
		const formatted = new Intl.DateTimeFormat(undefined, {
			day: 'numeric',
			month: 'short',
			year: 'numeric',
			timeZone: 'UTC',
		}).format(date);
		return bucketName === 'week' ? `Week of ${formatted}` : formatted;
	}

	function pluralLabel(label, value) {
		const lower = label.toLowerCase();
		if (value === 1 && lower.endsWith('s')) return lower.slice(0, -1);
		return lower;
	}

	function setDelta(element, values, index, bucketName) {
		element.classList.remove('is-up', 'is-down', 'is-flat');
		if (index === 0) {
			element.classList.add('is-flat');
			element.textContent = 'First point in range';
			return;
		}

		const current = values[index];
		const previous = values[index - 1];
		const delta = current - previous;
		const period = `previous ${bucketName}`;

		if (delta === 0) {
			element.classList.add('is-flat');
			element.textContent = `• No change vs ${period}`;
			return;
		}

		const direction = delta > 0 ? '▲' : '▼';
		const sign = delta > 0 ? '+' : '';
		let percent = '';
		if (previous > 0) {
			const pct = Math.round((delta / previous) * 100);
			percent = ` (${pct > 0 ? '+' : ''}${numberFormat.format(pct)}%)`;
		} else if (current > 0) {
			percent = ' (from 0)';
		}

		element.classList.add(delta > 0 ? 'is-up' : 'is-down');
		element.textContent = `${direction} ${sign}${numberFormat.format(delta)}${percent} vs ${period}`;
	}

	function enhanceChart(chart) {
		const values = String(chart.dataset.chartValues || '')
			.split(',')
			.filter(Boolean)
			.map(value => Number(value) || 0);
		if (!values.length) return;

		const start = Number(chart.dataset.chartStart || 0);
		const step = Number(chart.dataset.chartStep || 86400);
		const bucketName = chart.dataset.chartBucket || 'day';
		const label = chart.dataset.chartLabel || 'Activity';
		const peak = Math.max(...values, 1);
		const plot = chart.querySelector('.toc-chart__plot');
		const svg = chart.querySelector('svg');
		const hoverLine = chart.querySelector('.toc-chart__hover-line');
		const hoverPoint = chart.querySelector('.toc-chart__hover-point');
		const tooltip = chart.querySelector('.toc-chart__tooltip');
		const tooltipTitle = chart.querySelector('[data-chart-tooltip-title]');
		const tooltipDate = chart.querySelector('[data-chart-tooltip-date]');
		const tooltipValue = chart.querySelector('[data-chart-tooltip-value]');
		const tooltipDelta = chart.querySelector('[data-chart-tooltip-delta]');
		if (!plot || !svg || !hoverLine || !hoverPoint || !tooltip) return;

		const middleIndex = Math.floor((values.length - 1) / 2);
		const dateNodes = chart.querySelectorAll('[data-chart-date]');
		dateNodes.forEach(node => {
			const kind = node.dataset.chartDate;
			let index = 0;
			if (kind === 'middle') index = middleIndex;
			if (kind === 'end') index = values.length - 1;
			node.textContent = shortDateLabel(start + (index * step), bucketName);
		});

		function hideHover() {
			hoverLine.hidden = true;
			hoverPoint.hidden = true;
			tooltip.hidden = true;
		}

		function updateHover(event) {
			const svgRect = svg.getBoundingClientRect();
			if (!svgRect.width) return;
			const svgX = ((event.clientX - svgRect.left) / svgRect.width) * SVG_WIDTH;
			const stepX = values.length > 1 ? USABLE_WIDTH / (values.length - 1) : 0;
			const rawIndex = stepX ? Math.round((svgX - PAD) / stepX) : 0;
			const index = clamp(rawIndex, 0, values.length - 1);
			const value = values[index];
			const x = values.length > 1 ? PAD + (index * stepX) : PAD + (USABLE_WIDTH / 2);
			const y = SVG_HEIGHT - PAD - ((value / peak) * USABLE_HEIGHT);
			const epoch = start + (index * step);

			hoverLine.setAttribute('x1', x.toFixed(1));
			hoverLine.setAttribute('x2', x.toFixed(1));
			hoverPoint.setAttribute('cx', x.toFixed(1));
			hoverPoint.setAttribute('cy', y.toFixed(1));
			hoverLine.hidden = false;
			hoverPoint.hidden = false;

			tooltipTitle.textContent = label;
			tooltipDate.textContent = `${dateLabel(epoch, bucketName)} · UTC`;
			tooltipValue.textContent = `${numberFormat.format(value)} ${pluralLabel(label, value)}`;
			setDelta(tooltipDelta, values, index, bucketName);
			tooltip.hidden = false;

			const plotRect = plot.getBoundingClientRect();
			const tooltipRect = tooltip.getBoundingClientRect();
			const desiredLeft = event.clientX - plotRect.left + 14;
			const desiredTop = event.clientY - plotRect.top - tooltipRect.height - 12;
			const maxLeft = Math.max(8, plotRect.width - tooltipRect.width - 8);
			const maxTop = Math.max(8, plotRect.height - tooltipRect.height - 8);
			tooltip.style.left = `${clamp(desiredLeft, 8, maxLeft)}px`;
			tooltip.style.top = `${clamp(desiredTop, 8, maxTop)}px`;
		}

		plot.addEventListener('pointerenter', updateHover);
		plot.addEventListener('pointermove', updateHover);
		plot.addEventListener('pointerdown', updateHover);
		plot.addEventListener('pointerleave', hideHover);
	}

	document.querySelectorAll('.toc-chart[data-chart-values]').forEach(enhanceChart);
})();
