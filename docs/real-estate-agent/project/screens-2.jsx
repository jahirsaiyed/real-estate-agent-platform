// Screens part 2: My Offers, My Activity, My Documents, Smart Alerts, Viewings (buyer-facing)

const { Icon, fmtAED, fmtAEDShort } = window;

// ============ MY OFFERS (replaces CRM Pipeline) ============
function PipelineScreen() {
  const [offers, setOffers] = React.useState(window.MY_OFFERS);
  const [draggingId, setDraggingId] = React.useState(null);
  const [hoverStage, setHoverStage] = React.useState(null);

  const move = (id, stage) => {
    setOffers((os) => os.map((o) => o.id === id ? { ...o, stage } : o));
  };

  const propLookup = (id) => window.PROPERTIES.find((p) => p.id === id) || {};
  const totalActive = offers.filter((o) => o.stage === 'submitted' || o.stage === 'countered' || o.stage === 'drafting').length;
  const totalActiveValue = offers.
  filter((o) => o.stage !== 'rejected' && o.stage !== 'accepted').
  reduce((s, o) => s + o.myOffer, 0);

  return (
    <>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: 14 }}>
        <div>
          <h1 className="page">My offers</h1>
          <div className="page-sub">{totalActive} active · {fmtAEDShort(totalActiveValue)} on the table · drag to track stage</div>
        </div>
        <div style={{ display: 'flex', gap: 10 }}>
          <button className="btn"><Icon name="filter" size={14} /> Filter</button>
          <button className="btn btn-primary"><Icon name="plus" size={14} /> New offer</button>
        </div>
      </div>

      {/* Stage stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5,1fr)', gap: 10, marginBottom: 18 }}>
        {window.OFFER_STAGES.map((s) => {
          const count = offers.filter((o) => o.stage === s.key).length;
          return (
            <div key={s.key} className="glass-flat" style={{ padding: '10px 14px',
              borderTop: `2px solid ${s.accent}`, borderRadius: 10 }}>
              <div style={{ fontSize: 10, fontWeight: 700, textTransform: 'uppercase', letterSpacing: 0.55, color: '#94a3b8' }}>{s.label}</div>
              <div style={{ fontSize: 22, fontWeight: 700, fontFamily: 'var(--scp-font-mono)', color: s.accent, marginTop: 2 }}>{count}</div>
            </div>);

        })}
      </div>

      {/* Kanban */}
      <div style={{ display: 'flex', gap: 14, overflow: 'auto', paddingBottom: 8, minHeight: 480 }}>
        {window.OFFER_STAGES.map((s) =>
        <div key={s.key} className="kanban-col"
        onDragOver={(e) => {e.preventDefault();setHoverStage(s.key);}}
        onDragLeave={() => setHoverStage(null)}
        onDrop={(e) => {
          e.preventDefault();
          if (draggingId) move(draggingId, s.key);
          setDraggingId(null);setHoverStage(null);
        }}>
            <div className="glass-flat" style={{ padding: '10px 14px', marginBottom: 0,
            borderLeft: `3px solid ${s.accent}`,
            background: hoverStage === s.key ? 'rgba(34,211,238,0.08)' : undefined }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: 12, fontWeight: 700, letterSpacing: 0.04, textTransform: 'uppercase' }}>{s.label}</span>
                <span style={{ fontSize: 11, color: '#94a3b8', fontFamily: 'var(--scp-font-mono)' }}>{offers.filter((o) => o.stage === s.key).length}</span>
              </div>
            </div>
            {offers.filter((o) => o.stage === s.key).map((o) => {
            const p = propLookup(o.propertyId);
            const delta = (o.myOffer - o.listPrice) / o.listPrice * 100;
            return (
              <div key={o.id} className="kanban-card"
              draggable
              onDragStart={() => setDraggingId(o.id)}
              onDragEnd={() => {setDraggingId(null);setHoverStage(null);}}
              style={{ opacity: draggingId === o.id ? 0.4 : 1 }}>
                  <div style={{ display: 'flex', gap: 10, alignItems: 'flex-start' }}>
                    <div className={`prop-img ${p.img || 'img-1'}`} style={{ width: 42, height: 42, borderRadius: 8, marginBottom: 0, flexShrink: 0 }} />
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
                        <span style={{ fontWeight: 700, fontSize: 13, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{p.title}</span>
                      </div>
                      <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 2 }}>{p.area}</div>
                    </div>
                  </div>
                  <div style={{ marginTop: 10, padding: '8px 10px', background: 'rgba(0,0,0,0.25)', borderRadius: 8, fontFamily: 'var(--scp-font-mono)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 10, color: '#94a3b8' }}>
                      <span>List</span><span>{fmtAEDShort(o.listPrice)}</span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, color: '#22d3ee', fontWeight: 700, marginTop: 3 }}>
                      <span>You</span><span>{fmtAEDShort(o.myOffer)}</span>
                    </div>
                    {o.counter &&
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, color: '#fbbf24', fontWeight: 700, marginTop: 3 }}>
                        <span>Counter</span><span>{fmtAEDShort(o.counter)}</span>
                      </div>
                  }
                  </div>
                  <div style={{ display: 'flex', gap: 6, marginTop: 10, alignItems: 'center', flexWrap: 'wrap' }}>
                    <span className="chip chip-sm chip-mono" style={{
                    color: delta < -3 ? '#4ade80' : delta < 0 ? '#22d3ee' : '#94a3b8'
                  }}>{delta > 0 ? '+' : ''}{delta.toFixed(1)}% vs list</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 10, paddingTop: 10,
                  borderTop: '1px solid rgba(255,255,255,0.06)', fontSize: 10, color: '#64748b', fontFamily: 'var(--scp-font-mono)' }}>
                    <span>{o.id}</span>
                    <span>{o.updated}</span>
                  </div>
                </div>);

          })}
            {offers.filter((o) => o.stage === s.key).length === 0 &&
          <div style={{ padding: 24, textAlign: 'center', fontSize: 11, color: '#64748b',
            border: '1px dashed rgba(255,255,255,0.08)', borderRadius: 12 }}>
                Nothing here
              </div>
          }
          </div>
        )}
      </div>
    </>);

}

// ============ MY ACTIVITY (replaces Dashboard) ============
function DashboardScreen() {
  // Search-volume sparkline (saved-search activity)
  const trend = Array.from({ length: 30 }, (_, i) => 0.4 + Math.abs(Math.sin(i * 0.3)) * 0.7 + (i > 20 ? 0.4 : 0));
  const max = Math.max(...trend);

  return (
    <>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: 18 }}>
        <div>
          <h1 className="page">My activity</h1>
          <div className="page-sub">Sunday, 3 May · welcome back, Layla</div>
        </div>
        <div className="seg">
          <button className="active">7d</button>
          <button>30d</button>
          <button>90d</button>
        </div>
      </div>

      {/* KPI grid — buyer view */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 12, marginBottom: 18 }}>
        <KPI label="Saved homes" value="4" delta="2 with price drops" pos />
        <KPI label="Active offers" value="3" delta="1 awaiting response" pos />
        <KPI label="Viewings booked" value="5" delta="next: tomorrow 9am" pos />
        <KPI label="Pre-approval" value="AED 6.3M" delta="ENBD · 4.42% 25y" pos />
      </div>

      {/* Two-up: Search activity + Today */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 14, marginBottom: 18 }}>
        <div className="glass" style={{ padding: 18 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 18 }}>
            <div>
              <h3 className="eyebrow" style={{ margin: 0 }}>Saved-search activity · 30 days</h3>
              <div style={{ fontSize: 24, fontWeight: 700, fontFamily: 'var(--scp-font-mono)', marginTop: 4 }}>
                47 new matches
                <span style={{ fontSize: 12, color: '#4ade80', marginLeft: 10, fontWeight: 600 }}>+12.4%</span>
              </div>
            </div>
            <div className="chip chip-accent">
              <Icon name="sparkles" size={11} /> AI: market warming up
            </div>
          </div>
          <div style={{ height: 140, display: 'flex', alignItems: 'flex-end', gap: 3 }}>
            {trend.map((v, i) =>
            <div key={i} style={{ flex: 1, height: `${v / max * 100}%`, minHeight: 2,
              background: i > 23 ? 'linear-gradient(180deg,#5eead4,#22d3ee)' : 'rgba(34,211,238,0.35)',
              borderRadius: '3px 3px 0 0',
              boxShadow: i > 23 ? '0 0 6px rgba(34,211,238,0.4)' : 'none' }} />
            )}
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 10, color: '#64748b',
            fontFamily: 'var(--scp-font-mono)', marginTop: 6 }}>
            <span>04-04</span><span>05-03</span>
          </div>
        </div>

        <div className="glass" style={{ padding: 18, display: 'flex', flexDirection: 'column' }}>
          <h3 className="eyebrow">Up next</h3>
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 8, overflow: 'auto' }}>
            {window.MY_VIEWINGS.slice(0, 4).map((a, i) =>
            <div key={i} className="glass-flat" style={{ padding: '10px 12px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: 2 }}>
                  <span style={{ fontFamily: 'var(--scp-font-mono)', fontSize: 11, fontWeight: 700, color: '#22d3ee' }}>{a.time}</span>
                  <span style={{ fontSize: 10, textTransform: 'uppercase', letterSpacing: 0.4, color: '#94a3b8' }}>{a.kind}</span>
                </div>
                <div style={{ fontSize: 12, fontWeight: 600 }}>{a.title}</div>
                <div style={{ fontSize: 11, color: '#94a3b8' }}>{a.who}</div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* AI nudges + Recent activity */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
        <div className="glass" style={{ padding: 18 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 14 }}>
            <Icon name="sparkles" size={15} />
            <h3 className="eyebrow" style={{ margin: 0, color: '#22d3ee' }}>For your consideration</h3>
          </div>
          {[
          ['The Marina Penthouse seller countered at 8.2M. Comps support 8.05M as your walk-up — reply within 48h.', 'flame', '#f87171'],
          ['ENBD just dropped their 25y fixed rate by 0.15%. Worth re-running your pre-approval at 4.27%.', 'bar-chart', '#22d3ee'],
          ['2 new listings match "Marina sea-view 3BR" — both above 90% match. The 96% one is still under 8M.', 'sparkles', '#fbbf24']].
          map(([msg, ic, c], i) =>
          <div key={i} style={{ display: 'flex', gap: 10, alignItems: 'flex-start',
            padding: '12px 0', borderTop: i ? '1px solid rgba(255,255,255,0.06)' : 'none' }}>
              <div style={{ width: 28, height: 28, borderRadius: 8,
              background: `${c}1e`, border: `1px solid ${c}55`,
              color: c, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                <Icon name={ic} size={13} />
              </div>
              <div style={{ fontSize: 13, lineHeight: 1.5, color: '#cbd5e1' }}>{msg}</div>
            </div>
          )}
        </div>

        <div className="glass" style={{ padding: 18 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14 }}>
            <h3 className="eyebrow" style={{ margin: 0 }}>Recent activity</h3>
            <span className="chip chip-sm">live</span>
          </div>
          {window.MY_ACTIVITY.slice(0, 7).map((a, i) => {
            const colorMap = { alert: '#fbbf24', human: '#a78bfa', offer: '#f97316', doc: '#22d3ee', match: '#4ade80', mortgage: '#5eead4', self: '#94a3b8' };
            const c = colorMap[a.kind] || '#94a3b8';
            return (
              <div key={i} style={{ display: 'flex', gap: 10, alignItems: 'flex-start',
                padding: '10px 0', borderTop: i ? '1px solid rgba(255,255,255,0.06)' : 'none' }}>
                <div style={{ width: 6, height: 6, borderRadius: 999, background: c, marginTop: 6, flexShrink: 0, boxShadow: `0 0 6px ${c}88` }} />
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontSize: 12, color: '#cbd5e1', lineHeight: 1.5 }}>{a.msg}</div>
                  <div style={{ fontSize: 10, color: '#64748b', marginTop: 3, fontFamily: 'var(--scp-font-mono)' }}>
                    {a.t} · <span style={{ color: c }}>{a.who}</span>
                  </div>
                </div>
              </div>);

          })}
        </div>
      </div>
    </>);

}

function KPI({ label, value, delta, pos }) {
  return (
    <div className="glass" style={{ padding: '14px 18px' }}>
      <div style={{ fontSize: 10, fontWeight: 700, color: '#94a3b8', textTransform: 'uppercase', letterSpacing: 0.55, marginBottom: 6 }}>{label}</div>
      <div className="stat-num">{value}</div>
      <div className={pos ? 'stat-delta-up' : 'stat-delta-down'}>{delta}</div>
    </div>);

}

// ============ SMART ALERTS (replaces Automations) ============
function AutomationsScreen() {
  const [alerts, setAlerts] = React.useState(window.MY_ALERTS);
  const toggle = (id) => setAlerts((a) => a.map((x) => x.id === id ? { ...x, status: x.status === 'on' ? 'off' : 'on' } : x));
  const onCount = alerts.filter((a) => a.status === 'on').length;

  return (
    <>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: 18 }}>
        <div>
          <h1 className="page">Smart alerts</h1>
          <div className="page-sub">{onCount} of {alerts.length} active · Sceptre watches the market for you 24/7</div>
        </div>
        <button className="btn btn-primary"><Icon name="plus" size={14} /> New alert</button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill,minmax(320px,1fr))', gap: 14, marginBottom: 20 }}>
        {alerts.map((a) => {
          const on = a.status === 'on';
          return (
            <div key={a.id} className="glass" style={{ padding: 18, opacity: on ? 1 : 0.6 }}>
              <div style={{ display: 'flex', gap: 12, alignItems: 'flex-start', marginBottom: 12 }}>
                <div style={{ width: 38, height: 38, borderRadius: 10,
                  background: on ? 'rgba(34,211,238,0.12)' : 'rgba(255,255,255,0.04)',
                  border: `1px solid ${on ? 'rgba(34,211,238,0.30)' : 'rgba(255,255,255,0.10)'}`,
                  color: on ? '#22d3ee' : '#94a3b8',
                  display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <Icon name={a.icon} size={18} />
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 2 }}>
                    <span className="status-dot" style={{
                      background: on ? '#4ade80' : '#94a3b8',
                      animation: on ? 'scp-pulse 2s infinite' : 'none' }} />
                    <span style={{ fontWeight: 700, fontSize: 14 }}>{a.name}</span>
                  </div>
                  <div style={{ fontSize: 11, color: '#94a3b8', textTransform: 'uppercase', letterSpacing: 0.4 }}>{on ? 'watching' : 'paused'}</div>
                </div>
                <button onClick={() => toggle(a.id)} className="btn-icon" style={{
                  width: 42, height: 24, borderRadius: 999,
                  border: `1px solid ${on ? 'rgba(34,211,238,0.40)' : 'rgba(255,255,255,0.12)'}`,
                  background: on ? 'rgba(34,211,238,0.20)' : 'rgba(255,255,255,0.04)',
                  position: 'relative', cursor: 'pointer', padding: 0 }}>
                  <span style={{ position: 'absolute', top: 2, left: on ? 20 : 2, width: 18, height: 18, borderRadius: 999,
                    background: on ? '#22d3ee' : '#94a3b8', transition: 'left 0.2s ease',
                    boxShadow: on ? '0 0 8px rgba(34,211,238,0.5)' : 'none' }} />
                </button>
              </div>
              <div style={{ fontSize: 12, color: '#cbd5e1', lineHeight: 1.5, marginBottom: 14 }}>{a.desc}</div>
              <div style={{ padding: '10px 12px',
                background: 'rgba(0,0,0,0.25)', borderRadius: 10 }}>
                <div style={{ fontSize: 9, color: '#94a3b8', letterSpacing: 0.55, textTransform: 'uppercase', fontWeight: 700 }}>Last triggered</div>
                <div style={{ fontSize: 11, color: on ? '#5eead4' : '#64748b', fontFamily: 'var(--scp-font-mono)', marginTop: 3 }}>
                  {a.lastFire}
                </div>
                <div style={{ fontSize: 9, color: '#64748b', letterSpacing: 0.55, textTransform: 'uppercase', fontWeight: 700, marginTop: 8, fontFamily: 'var(--scp-font-mono)' }}>
                  {a.runs} fires · last 30d
                </div>
              </div>
            </div>);

        })}

        {/* Empty add card */}
        <div className="glass" style={{ padding: 18, border: '1px dashed rgba(255,255,255,0.14)',
          background: 'transparent', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
          minHeight: 200, cursor: 'pointer', color: '#94a3b8' }}>
          <Icon name="plus" size={26} />
          <div style={{ fontSize: 13, marginTop: 10, fontWeight: 600 }}>Create a new alert</div>
          <div style={{ fontSize: 11, color: '#64748b', marginTop: 4, textAlign: 'center', maxWidth: 200 }}>
            Describe what to watch — Sceptre handles the rest
          </div>
        </div>
      </div>

      {/* Live activity */}
      <div className="glass" style={{ padding: 18 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14 }}>
          <h3 className="eyebrow" style={{ margin: 0 }}>What Sceptre is doing right now</h3>
          <span className="chip chip-sm"><span className="status-dot pulse" style={{ background: '#4ade80' }} /> streaming</span>
        </div>
        <div style={{ background: 'rgba(0,0,0,0.4)', borderRadius: 10, padding: '12px 14px',
          fontFamily: 'var(--scp-font-mono)', fontSize: 11, lineHeight: 1.7,
          maxHeight: 180, overflow: 'auto' }}>
          {[
          ['09:42:18', 'price.watch', 'scanned 1,840 listings · 2 dropped 3%+ in your areas'],
          ['09:42:01', 'match.engine', 're-scored "Marina sea-view 3BR" · P-1042 still top match (96%)'],
          ['09:38:04', 'market.brief', 'generated comp report for Saadiyat villas · +3.8% MoM'],
          ['09:36:51', 'rate.watch', 'polled ENBD, Mashreq, FAB rates · ENBD -0.15% since yesterday'],
          ['09:32:11', 'offer.watch', 'Marina Penthouse counter-offer detected · pushed alert'],
          ['09:28:33', 'viewing.watch', 'viewing in 24h · drafted reminder + transit estimate'],
          ['09:14:02', 'match.engine', '2 new listings indexed · auto-scored against your prefs'],
          ['09:08:47', 'market.brief', 'market report regenerated · Saadiyat villas · +3.8% MoM']].
          map(([t, who, msg], i) =>
          <div key={i}>
              <span style={{ color: '#64748b' }}>{t}</span>{' '}
              <span style={{ color: '#22d3ee' }}>{who}</span>{' '}
              <span style={{ color: '#cbd5e1' }}>{msg}</span>
            </div>
          )}
        </div>
      </div>
    </>);

}

// ============ MY DOCUMENTS ============
function DocumentsScreen() {
  const statusMap = {
    'awaiting-you': { c: '#f97316', l: 'Needs you' },
    'awaiting-bank': { c: '#fbbf24', l: 'Awaiting bank' },
    'submitted': { c: '#22d3ee', l: 'Submitted' },
    'completed': { c: '#4ade80', l: 'Completed' },
    'auto-generated': { c: '#a78bfa', l: 'Auto-generated' }
  };

  return (
    <>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: 18 }}>
        <div>
          <h1 className="page">My Documents</h1>
          <div className="page-sub">Sceptre auto-drafts your paperwork · review and sign</div>
        </div>
        <div style={{ display: 'flex', gap: 10 }}>
          <button className="btn"><Icon name="filter" size={14} /> Filter</button>
          <button className="btn btn-primary"><Icon name="sparkles" size={14} /> Auto-draft new</button>
        </div>
      </div>

      {/* Quick stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 12, marginBottom: 18 }}>
        <KPI label="Awaiting you" value="2" delta="signature & review" pos />
        <KPI label="Auto-drafted" value="2" delta="ready for review" pos />
        <KPI label="In progress" value="6" delta="across 4 properties" pos />
        <KPI label="Total value" value="AED 28.4M" delta="this quarter" pos />
      </div>

      <div className="glass" style={{ padding: 0, overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
          <thead>
            <tr>
              {['Document', 'Kind', 'Property', 'Value', 'Status', 'Progress', 'Action', ''].map((h, i) =>
              <th key={h} style={{ textAlign: i === 3 || i === 5 ? 'right' : 'left',
                padding: '12px 16px', fontSize: 10, fontWeight: 700,
                textTransform: 'uppercase', letterSpacing: 0.55, color: '#94a3b8',
                borderBottom: '1px solid rgba(255,255,255,0.08)',
                background: 'rgba(255,255,255,0.02)' }}>{h}</th>
              )}
            </tr>
          </thead>
          <tbody>
            {window.MY_DOCUMENTS.map((d) => {
              const sm = statusMap[d.status] || { c: '#94a3b8', l: d.status };
              return (
                <tr key={d.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.04)', cursor: 'pointer' }}
                onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(255,255,255,0.03)'}
                onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}>
                  <td style={{ padding: '14px 16px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                      <div style={{ width: 32, height: 32, borderRadius: 8, background: 'rgba(255,255,255,0.04)',
                        border: '1px solid rgba(255,255,255,0.08)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#94a3b8' }}>
                        <Icon name="file" size={14} />
                      </div>
                      <div>
                        <div style={{ fontWeight: 600 }}>{d.name}</div>
                        <div style={{ fontSize: 10, fontFamily: 'var(--scp-font-mono)', color: '#64748b' }}>{d.id}</div>
                      </div>
                    </div>
                  </td>
                  <td style={{ padding: '14px 16px', color: '#cbd5e1' }}>{d.kind}</td>
                  <td style={{ padding: '14px 16px', fontFamily: 'var(--scp-font-mono)', fontSize: 11, color: '#94a3b8' }}>{d.property}</td>
                  <td style={{ padding: '14px 16px', textAlign: 'right', fontFamily: 'var(--scp-font-mono)', color: '#22d3ee', fontWeight: 700 }}>
                    {fmtAEDShort(d.value)}
                  </td>
                  <td style={{ padding: '14px 16px' }}>
                    <span style={{ display: 'inline-block', padding: '2px 9px', borderRadius: 999,
                      fontSize: 10, fontWeight: 700, textTransform: 'uppercase', letterSpacing: 0.45,
                      background: sm.c + '1e', color: sm.c, border: `1px solid ${sm.c}44` }}>
                      {sm.l}
                    </span>
                  </td>
                  <td style={{ padding: '14px 16px', textAlign: 'right' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, justifyContent: 'flex-end' }}>
                      <div style={{ width: 80, height: 5, borderRadius: 3, background: 'rgba(255,255,255,0.06)', overflow: 'hidden' }}>
                        <div style={{ width: `${d.progress}%`, height: '100%',
                          background: 'linear-gradient(90deg,#5eead4,#22d3ee)',
                          boxShadow: '0 0 6px rgba(34,211,238,0.3)' }} />
                      </div>
                      <span style={{ fontFamily: 'var(--scp-font-mono)', fontSize: 10, color: '#94a3b8', width: 30 }}>{d.progress}%</span>
                    </div>
                  </td>
                  <td style={{ padding: '14px 16px', color: d.action ? '#fbbf24' : '#64748b', fontSize: 11 }}>
                    {d.action || <span style={{ color: '#64748b' }}>—</span>}
                  </td>
                  <td style={{ padding: '14px 16px', textAlign: 'right' }}>
                    <button className="btn-icon" style={{ width: 28, height: 28, background: 'transparent',
                      border: '1px solid rgba(255,255,255,0.08)', borderRadius: 7, color: '#94a3b8', cursor: 'pointer' }}>
                      <Icon name="chevR" size={13} />
                    </button>
                  </td>
                </tr>);

            })}
          </tbody>
        </table>
      </div>
    </>);

}

// ============ VIEWINGS (calendar) ============
function CalendarScreen() {
  const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  const dates = [3, 4, 5, 6, 7, 8, 9];
  const today = 3;

  // Buyer's own viewings + calls + offer reviews
  const events = [
  { day: 1, start: 9, dur: 1, title: 'Marina Penthouse', who: 'with Layla', kind: 'viewing' },
  { day: 1, start: 11.5, dur: 0.5, title: 'ENBD pre-approval', who: 'Salem Al Marri', kind: 'call' },
  { day: 2, start: 10, dur: 1, title: 'Comparable walkthroughs', who: 'self-guided', kind: 'work' },
  { day: 3, start: 14, dur: 1.5, title: 'Downtown Burj View', who: 'with Layla', kind: 'viewing' },
  { day: 4, start: 16.5, dur: 0.5, title: 'Saadiyat offer review', who: 'with Sceptre AI', kind: 'offer' },
  { day: 5, start: 11, dur: 2, title: 'Saadiyat Beach Villa', who: 'with Omar', kind: 'viewing' },
  { day: 5, start: 14, dur: 1, title: 'Mortgage docs check', who: 'with Sceptre AI', kind: 'work' },
  { day: 6, start: 10, dur: 1.5, title: 'Al Reem Townhouse', who: 'with Omar', kind: 'viewing' }];


  const kindColor = {
    viewing: '#22d3ee', call: '#a78bfa', offer: '#f97316', closing: '#4ade80', work: '#94a3b8'
  };

  const hours = [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18];

  return (
    <>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: 18 }}>
        <div>
          <h1 className="page">Viewings</h1>
          <div className="page-sub">Week of 3-9 May · 8 events scheduled · all auto-confirmed by Sceptre</div>
        </div>
        <div style={{ display: 'flex', gap: 10 }}>
          <div className="seg">
            <button>Day</button>
            <button className="active">Week</button>
            <button>Month</button>
          </div>
          <button className="btn btn-primary"><Icon name="plus" size={14} /> Schedule</button>
        </div>
      </div>

      <div className="glass" style={{ padding: 0, overflow: 'hidden' }}>
        {/* Day headers */}
        <div style={{ display: 'grid', gridTemplateColumns: '60px repeat(7,1fr)',
          borderBottom: '1px solid rgba(255,255,255,0.08)', background: 'rgba(0,0,0,0.2)' }}>
          <div />
          {days.map((d, i) =>
          <div key={d} style={{ padding: '12px 14px', textAlign: 'center',
            borderLeft: '1px solid rgba(255,255,255,0.05)' }}>
              <div style={{ fontSize: 10, color: '#94a3b8', letterSpacing: 0.55, textTransform: 'uppercase', fontWeight: 700 }}>{d}</div>
              <div style={{ fontSize: 18, fontWeight: 700, marginTop: 2,
              color: dates[i] === today ? '#22d3ee' : '#f8fafc',
              fontFamily: 'var(--scp-font-mono)' }}>{dates[i]}</div>
            </div>
          )}
        </div>
        {/* Body */}
        <div style={{ display: 'grid', gridTemplateColumns: '60px repeat(7,1fr)', position: 'relative', minHeight: 520 }}>
          {/* Hours */}
          <div>
            {hours.map((h) =>
            <div key={h} style={{ height: 48, padding: '4px 8px', fontSize: 10, color: '#64748b',
              fontFamily: 'var(--scp-font-mono)', textAlign: 'right',
              borderBottom: '1px solid rgba(255,255,255,0.04)' }}>{h}:00</div>
            )}
          </div>
          {/* Day columns */}
          {days.map((d, di) =>
          <div key={d} style={{ borderLeft: '1px solid rgba(255,255,255,0.05)', position: 'relative' }}>
              {hours.map((h) =>
            <div key={h} style={{ height: 48, borderBottom: '1px solid rgba(255,255,255,0.04)' }} />
            )}
              {events.filter((e) => e.day === di).map((e, i) => {
              const top = (e.start - 8) * 48;
              const height = e.dur * 48 - 4;
              const c = kindColor[e.kind];
              return (
                <div key={i} style={{ position: 'absolute', top: top + 2, left: 4, right: 4, height,
                  background: `linear-gradient(165deg, ${c}28, ${c}12)`,
                  border: `1px solid ${c}55`, borderLeft: `3px solid ${c}`,
                  borderRadius: 6, padding: '4px 8px', cursor: 'pointer',
                  boxShadow: `0 4px 10px rgba(0,0,0,0.2), inset 0 0.5px 0 rgba(255,255,255,0.10)`,
                  overflow: 'hidden' }}>
                    <div style={{ fontSize: 11, fontWeight: 700, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{e.title}</div>
                    <div style={{ fontSize: 10, color: '#94a3b8', marginTop: 1, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{e.who}</div>
                  </div>);

            })}
            </div>
          )}
        </div>
      </div>
    </>);

}

Object.assign(window, { PipelineScreen, DashboardScreen, AutomationsScreen, DocumentsScreen, CalendarScreen });