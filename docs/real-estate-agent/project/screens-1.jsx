// Screens part 1: Browse, Property Detail, AI Chat

const { Icon, ArchLines, fmtAED, fmtAEDShort } = window;

// ============ BROWSE / SEARCH ============
function BrowseScreen({ onOpenProperty, onOpenChat, view, setView }) {
  const [filters, setFilters] = React.useState({
    emirate: 'All', type: 'All', priceMin: 0, priceMax: 20_000_000, beds: 0,
  });
  const [hover, setHover] = React.useState(null);
  const [savedSet, setSavedSet] = React.useState(new Set(['P-1042','P-1015']));

  const filtered = window.PROPERTIES.filter(p => {
    if (filters.emirate !== 'All' && p.emirate !== filters.emirate) return false;
    if (filters.type !== 'All' && p.type !== filters.type) return false;
    if (p.price < filters.priceMin || p.price > filters.priceMax) return false;
    if (filters.beds && p.beds < filters.beds) return false;
    return true;
  });

  const toggleSave = (id, e) => {
    e.stopPropagation();
    const next = new Set(savedSet);
    next.has(id) ? next.delete(id) : next.add(id);
    setSavedSet(next);
  };

  return (
    <>
      {/* Header */}
      <div style={{display:'flex',justifyContent:'space-between',alignItems:'flex-end',marginBottom:18}}>
        <div>
          <h1 className="page">Find a home</h1>
          <div className="page-sub">{filtered.length} listings across the UAE · curated by Sceptre AI</div>
        </div>
        <div style={{display:'flex',gap:10,alignItems:'center'}}>
          <button className="btn" onClick={onOpenChat}>
            <Icon name="sparkles" size={14}/> Ask the agent
          </button>
          <div className="seg">
            <button className={view==='grid'?'active':''} onClick={()=>setView('grid')}>
              <Icon name="grid" size={13}/>
            </button>
            <button className={view==='split'?'active':''} onClick={()=>setView('split')}>
              <Icon name="map" size={13}/>
            </button>
          </div>
        </div>
      </div>

      {/* Filter bar */}
      <div className="glass" style={{padding:'14px 16px',marginBottom:18,display:'flex',gap:12,alignItems:'center',flexWrap:'wrap'}}>
        <div style={{position:'relative',flex:'1 1 240px',minWidth:200}}>
          <input className="input" style={{paddingLeft:36}} placeholder="Try 'sea view 3BR under 5M in Dubai Marina'"/>
          <div style={{position:'absolute',left:12,top:'50%',transform:'translateY(-50%)',color:'#94a3b8'}}>
            <Icon name="search" size={16}/>
          </div>
        </div>
        <SelectMini value={filters.emirate} onChange={v=>setFilters(f=>({...f,emirate:v}))}
          options={['All',...window.EMIRATES]} label="Emirate"/>
        <SelectMini value={filters.type} onChange={v=>setFilters(f=>({...f,type:v}))}
          options={['All','Apartment','Villa','Penthouse','Townhouse']} label="Type"/>
        <SelectMini value={String(filters.beds)} onChange={v=>setFilters(f=>({...f,beds:Number(v)}))}
          options={['0','1','2','3','4','5']} label="Min beds" displayMap={{'0':'Any'}}/>
        <div style={{display:'flex',alignItems:'center',gap:8,paddingLeft:10,borderLeft:'1px solid rgba(255,255,255,0.08)'}}>
          <span className="chip chip-accent chip-sm mono">AI MATCH ON</span>
        </div>
      </div>

      {/* Active filter chips */}
      <div style={{display:'flex',gap:8,flexWrap:'wrap',marginBottom:18}}>
        <span className="chip">Sea view</span>
        <span className="chip">Smart home</span>
        <span className="chip">Walkable area</span>
        <span className="chip" style={{cursor:'pointer',opacity:0.6}}>+ add preference</span>
      </div>

      {/* Content layout */}
      {view === 'split' ? (
        <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:16,minHeight:540}}>
          {/* Map */}
          <div className="glass map-canvas" style={{borderRadius:16,minHeight:540,position:'sticky',top:0}}>
            <div className="map-grid"/>
            {/* "Coastline" curve */}
            <svg style={{position:'absolute',inset:0,width:'100%',height:'100%'}} viewBox="0 0 100 100" preserveAspectRatio="none">
              <path d="M0,55 Q20,45 35,52 T70,48 T100,42" stroke="rgba(34,211,238,0.25)" strokeWidth="0.4" fill="none"/>
              <path d="M0,58 Q20,48 35,55 T70,51 T100,45" stroke="rgba(34,211,238,0.10)" strokeWidth="0.3" fill="none"/>
            </svg>
            {/* labels */}
            <div style={{position:'absolute',top:'15%',left:'18%',fontSize:10,color:'rgba(148,163,184,0.5)',letterSpacing:1,textTransform:'uppercase'}}>Dubai</div>
            <div style={{position:'absolute',top:'12%',left:'62%',fontSize:10,color:'rgba(148,163,184,0.5)',letterSpacing:1,textTransform:'uppercase'}}>Sharjah</div>
            <div style={{position:'absolute',top:'30%',left:'82%',fontSize:10,color:'rgba(148,163,184,0.5)',letterSpacing:1,textTransform:'uppercase'}}>Ajman</div>
            <div style={{position:'absolute',top:'62%',left:'18%',fontSize:10,color:'rgba(148,163,184,0.5)',letterSpacing:1,textTransform:'uppercase'}}>Abu Dhabi</div>
            <div style={{position:'absolute',top:'78%',left:'72%',fontSize:10,color:'rgba(148,163,184,0.5)',letterSpacing:1,textTransform:'uppercase'}}>RAK</div>

            {filtered.map(p => (
              <div key={p.id} className={`map-pin ${hover===p.id?'active':''}`}
                style={{left:`${p.lng}%`,top:`${p.lat}%`}}
                onMouseEnter={()=>setHover(p.id)} onMouseLeave={()=>setHover(null)}
                onClick={()=>onOpenProperty(p)}>
                <div className="pin-body">{fmtAEDShort(p.price)}</div>
              </div>
            ))}

            {/* Map legend */}
            <div style={{position:'absolute',bottom:14,left:14,display:'flex',gap:6,alignItems:'center',
              padding:'6px 10px',borderRadius:999,background:'rgba(0,0,0,0.5)',border:'1px solid rgba(255,255,255,0.08)',
              backdropFilter:'blur(12px)',fontSize:10,color:'#94a3b8'}}>
              <span className="status-dot" style={{width:6,height:6}}/> {filtered.length} active
            </div>
          </div>

          {/* List */}
          <div style={{display:'flex',flexDirection:'column',gap:12,maxHeight:540,overflow:'auto',paddingRight:4}}>
            {filtered.map(p => (
              <PropertyRow key={p.id} prop={p}
                onClick={()=>onOpenProperty(p)}
                onHover={()=>setHover(p.id)}
                onLeave={()=>setHover(null)}
                hovered={hover===p.id}
                saved={savedSet.has(p.id)}
                onToggleSave={e=>toggleSave(p.id,e)}/>
            ))}
          </div>
        </div>
      ) : (
        <div className="prop-grid">
          {filtered.map(p => (
            <PropertyCard key={p.id} prop={p}
              onClick={()=>onOpenProperty(p)}
              saved={savedSet.has(p.id)}
              onToggleSave={e=>toggleSave(p.id,e)}/>
          ))}
        </div>
      )}
    </>
  );
}

function PropertyCard({ prop, onClick, saved, onToggleSave }) {
  const variant = ((parseInt(prop.id.slice(-2)) % 3) + 1);
  return (
    <div className="glass prop-card" style={{padding:14}} onClick={onClick}>
      <div className={`prop-img ${prop.img}`}>
        <ArchLines variant={variant}/>
        <div style={{position:'absolute',top:10,left:10,display:'flex',gap:6}}>
          <span className="chip chip-accent chip-sm">
            <Icon name="sparkles" size={10}/> {prop.match}% match
          </span>
        </div>
        <button onClick={onToggleSave} className="btn-icon"
          style={{position:'absolute',top:10,right:10,width:32,height:32,borderRadius:999,
            background:saved?'rgba(248,113,113,0.20)':'rgba(0,0,0,0.5)',
            border:`1px solid ${saved?'rgba(248,113,113,0.5)':'rgba(255,255,255,0.15)'}`,
            color:saved?'#f87171':'#f8fafc',cursor:'pointer',backdropFilter:'blur(12px)'}}>
          <Icon name="heart" size={14}/>
        </button>
        <div style={{position:'absolute',bottom:10,left:10,display:'flex',gap:6}}>
          <span className="chip chip-sm" style={{background:'rgba(0,0,0,0.6)',backdropFilter:'blur(12px)'}}>
            {prop.type}
          </span>
        </div>
      </div>
      <div style={{display:'flex',justifyContent:'space-between',alignItems:'flex-start',marginBottom:6}}>
        <div style={{fontWeight:700,fontSize:15,lineHeight:1.3}}>{prop.title}</div>
        <div style={{fontFamily:'var(--scp-font-mono)',fontWeight:700,fontSize:14,color:'#22d3ee',whiteSpace:'nowrap',marginLeft:10}}>
          {fmtAEDShort(prop.price)}
        </div>
      </div>
      <div style={{fontSize:12,color:'#94a3b8',marginBottom:10,display:'flex',alignItems:'center',gap:5}}>
        <Icon name="pin" size={12}/> {prop.area} · {prop.emirate}
      </div>
      <div style={{display:'flex',gap:14,fontSize:12,color:'#cbd5e1',paddingTop:10,borderTop:'1px solid rgba(255,255,255,0.06)'}}>
        <span style={{display:'flex',alignItems:'center',gap:5}}><Icon name="bed" size={13}/> {prop.beds}</span>
        <span style={{display:'flex',alignItems:'center',gap:5}}><Icon name="bath" size={13}/> {prop.baths}</span>
        <span style={{display:'flex',alignItems:'center',gap:5}}><Icon name="sqft" size={13}/> <span className="mono">{prop.sqft.toLocaleString()}</span> sqft</span>
        <span style={{marginLeft:'auto',color:'#94a3b8',fontSize:11}}>{prop.listed}</span>
      </div>
    </div>
  );
}

function PropertyRow({ prop, onClick, onHover, onLeave, hovered, saved, onToggleSave }) {
  const variant = ((parseInt(prop.id.slice(-2)) % 3) + 1);
  return (
    <div className="glass prop-card" onClick={onClick} onMouseEnter={onHover} onMouseLeave={onLeave}
      style={{padding:12,display:'flex',gap:14,
        borderColor:hovered?'rgba(34,211,238,0.45)':'rgba(255,255,255,0.10)'}}>
      <div className={`prop-img ${prop.img}`} style={{width:140,height:104,marginBottom:0,flexShrink:0,borderRadius:10}}>
        <ArchLines variant={variant}/>
      </div>
      <div style={{flex:1,minWidth:0,display:'flex',flexDirection:'column'}}>
        <div style={{display:'flex',justifyContent:'space-between',alignItems:'flex-start',marginBottom:4}}>
          <div style={{fontWeight:700,fontSize:14,lineHeight:1.3}}>{prop.title}</div>
          <div style={{fontFamily:'var(--scp-font-mono)',fontWeight:700,fontSize:13,color:'#22d3ee',whiteSpace:'nowrap',marginLeft:10}}>
            {fmtAEDShort(prop.price)}
          </div>
        </div>
        <div style={{fontSize:11,color:'#94a3b8',marginBottom:'auto',display:'flex',alignItems:'center',gap:5}}>
          <Icon name="pin" size={11}/> {prop.area}
        </div>
        <div style={{display:'flex',gap:10,fontSize:11,color:'#cbd5e1',marginTop:8}}>
          <span><Icon name="bed" size={11}/> {prop.beds}</span>
          <span><Icon name="bath" size={11}/> {prop.baths}</span>
          <span className="mono">{prop.sqft.toLocaleString()} sqft</span>
          <span style={{marginLeft:'auto'}} className="chip chip-accent chip-sm">{prop.match}% match</span>
        </div>
      </div>
    </div>
  );
}

function SelectMini({ value, onChange, options, label, displayMap }) {
  return (
    <div style={{display:'flex',flexDirection:'column',gap:2}}>
      <span style={{fontSize:9,fontWeight:700,color:'#94a3b8',letterSpacing:0.55,textTransform:'uppercase'}}>{label}</span>
      <select value={value} onChange={e=>onChange(e.target.value)}
        style={{padding:'7px 10px',borderRadius:8,border:'1px solid rgba(255,255,255,0.10)',
          background:'rgba(0,0,0,0.28)',color:'#f8fafc',fontSize:12,outline:'none',fontFamily:'inherit',cursor:'pointer'}}>
        {options.map(o => <option key={o} value={o} style={{background:'#1a1a20'}}>{(displayMap&&displayMap[o])||o}</option>)}
      </select>
    </div>
  );
}

// ============ PROPERTY DETAIL ============
function PropertyDetailScreen({ prop, onBack, onOpenChat }) {
  const [tab, setTab] = React.useState('overview');
  const variant = ((parseInt(prop.id.slice(-2)) % 3) + 1);
  const agent = window.AGENTS.find(a => a.name === prop.agent) || window.AGENTS[0];

  return (
    <>
      <div style={{display:'flex',alignItems:'center',gap:8,marginBottom:14,fontSize:12,color:'#94a3b8'}}>
        <button onClick={onBack} style={{background:'none',border:'none',color:'#94a3b8',cursor:'pointer',
          fontSize:12,padding:0,fontFamily:'inherit',display:'inline-flex',alignItems:'center',gap:4}}>
          <Icon name="chevL" size={14}/> Listings
        </button>
        <span>·</span>
        <span>{prop.emirate}</span>
        <span>·</span>
        <span>{prop.area}</span>
        <span style={{marginLeft:'auto',fontFamily:'var(--scp-font-mono)',fontSize:11,color:'#64748b'}}>{prop.id}</span>
      </div>

      {/* Hero */}
      <div className={`hero ${prop.img}`}>
        <ArchLines variant={variant}/>
        <div className="overlay"/>
        <div style={{position:'absolute',top:18,left:18,display:'flex',gap:8}}>
          <span className="chip chip-accent">
            <Icon name="sparkles" size={11}/> {prop.match}% match for you
          </span>
          <span className="chip">{prop.type}</span>
          <span className="chip mono">{prop.trend} YoY</span>
        </div>
        <div style={{position:'absolute',top:18,right:18,display:'flex',gap:8}}>
          <button className="btn btn-icon" style={{background:'rgba(0,0,0,0.5)',backdropFilter:'blur(12px)'}}>
            <Icon name="share" size={15}/>
          </button>
          <button className="btn btn-icon" style={{background:'rgba(0,0,0,0.5)',backdropFilter:'blur(12px)'}}>
            <Icon name="heart" size={15}/>
          </button>
        </div>
        <div style={{position:'absolute',bottom:22,left:22,right:22}}>
          <div style={{fontSize:30,fontWeight:700,letterSpacing:-0.5,marginBottom:6,textShadow:'0 2px 12px rgba(0,0,0,0.6)'}}>{prop.title}</div>
          <div style={{display:'flex',gap:18,fontSize:13,color:'#e2e8f0'}}>
            <span style={{display:'flex',alignItems:'center',gap:6}}><Icon name="pin" size={14}/> {prop.area}, {prop.emirate}</span>
            <span style={{display:'flex',alignItems:'center',gap:6}}><Icon name="bed" size={14}/> {prop.beds} bed</span>
            <span style={{display:'flex',alignItems:'center',gap:6}}><Icon name="bath" size={14}/> {prop.baths} bath</span>
            <span style={{display:'flex',alignItems:'center',gap:6,fontFamily:'var(--scp-font-mono)'}}><Icon name="sqft" size={14}/> {prop.sqft.toLocaleString()} sqft</span>
          </div>
        </div>
      </div>

      {/* 3 thumbs */}
      <div style={{display:'grid',gridTemplateColumns:'repeat(3,1fr)',gap:10,marginTop:10,marginBottom:24}}>
        {[1,2,3].map(i => (
          <div key={i} className={`prop-img ${prop.img}`} style={{height:90,marginBottom:0,borderRadius:10,opacity:0.85}}>
            <ArchLines variant={i}/>
          </div>
        ))}
      </div>

      {/* Body grid */}
      <div style={{display:'grid',gridTemplateColumns:'1fr 320px',gap:20}}>
        {/* Main column */}
        <div>
          <div style={{display:'flex',justifyContent:'space-between',alignItems:'flex-end',marginBottom:14}}>
            <div>
              <div style={{fontSize:11,color:'#94a3b8',fontWeight:700,textTransform:'uppercase',letterSpacing:0.55,marginBottom:4}}>Listing price</div>
              <div style={{fontSize:32,fontWeight:700,letterSpacing:-0.5,fontFamily:'var(--scp-font-mono)',color:'#22d3ee'}}>{fmtAED(prop.price)}</div>
              <div style={{fontSize:12,color:'#94a3b8',fontFamily:'var(--scp-font-mono)',marginTop:4}}>
                AED {Math.round(prop.price/prop.sqft).toLocaleString()} / sqft
              </div>
            </div>
          </div>

          <div className="tabs" style={{marginBottom:18}}>
            {[['overview','Overview'],['features','Features'],['valuation','AI Valuation'],['neighborhood','Neighborhood']].map(([k,l]) => (
              <button key={k} className={`tab ${tab===k?'active':''}`} onClick={()=>setTab(k)}>{l}</button>
            ))}
          </div>

          {tab==='overview' && (
            <div style={{fontSize:14,lineHeight:1.7,color:'#cbd5e1'}}>
              <p style={{margin:'0 0 16px'}}>{prop.desc}</p>
              <h3 className="eyebrow" style={{marginTop:24}}>Listed</h3>
              <p style={{margin:0}}>{prop.listed} · last price update 4 days ago</p>
            </div>
          )}

          {tab==='features' && (
            <div style={{display:'grid',gridTemplateColumns:'repeat(2,1fr)',gap:10}}>
              {prop.features.map(f => (
                <div key={f} className="glass-flat" style={{padding:'10px 14px',display:'flex',alignItems:'center',gap:10}}>
                  <div style={{width:28,height:28,borderRadius:8,background:'rgba(34,211,238,0.12)',
                    border:'1px solid rgba(34,211,238,0.3)',display:'flex',alignItems:'center',justifyContent:'center',color:'#22d3ee'}}>
                    <Icon name="check" size={14}/>
                  </div>
                  <span style={{fontSize:13}}>{f}</span>
                </div>
              ))}
            </div>
          )}

          {tab==='valuation' && (
            <div className="glass-flat" style={{padding:18}}>
              <div style={{display:'flex',alignItems:'center',gap:8,marginBottom:14}}>
                <Icon name="sparkles" size={16}/>
                <h3 className="eyebrow" style={{margin:0,color:'#22d3ee'}}>Sceptre AI valuation</h3>
              </div>
              <div style={{display:'grid',gridTemplateColumns:'repeat(3,1fr)',gap:14,marginBottom:18}}>
                <ValStat label="Estimated value" value={fmtAEDShort(prop.price * 1.04)} delta="+4.0%" pos/>
                <ValStat label="Listed price" value={fmtAEDShort(prop.price)} delta="benchmark"/>
                <ValStat label="Comparable median" value={fmtAEDShort(prop.price * 0.98)} delta="-2.0%"/>
              </div>
              <div style={{fontSize:13,lineHeight:1.6,color:'#cbd5e1'}}>
                Based on 14 comparable properties sold in {prop.area} over the last 6 months. Listing is priced
                slightly below model estimate ({prop.trend} YoY), suggesting strong buy-side opportunity.
              </div>
              {/* tiny bar comp chart */}
              <div style={{marginTop:14}}>
                <div style={{fontSize:10,color:'#94a3b8',marginBottom:6,fontWeight:700,textTransform:'uppercase',letterSpacing:0.55}}>Recent comparables (AED M)</div>
                <div style={{display:'flex',gap:4,alignItems:'flex-end',height:60}}>
                  {[0.85,0.92,1.0,0.95,1.05,0.98,1.02,0.91,1.06,0.94,1.00,0.97,1.04,0.96].map((v,i)=>(
                    <div key={i} style={{flex:1,height:`${v*55}%`,
                      background:i===6?'linear-gradient(180deg,#5eead4,#22d3ee)':'rgba(34,211,238,0.35)',
                      borderRadius:'2px 2px 0 0',
                      boxShadow:i===6?'0 0 8px rgba(34,211,238,0.5)':'none'}}/>
                  ))}
                </div>
              </div>
            </div>
          )}

          {tab==='neighborhood' && (
            <div style={{display:'grid',gridTemplateColumns:'repeat(2,1fr)',gap:10}}>
              {[
                ['Walk score','82 / 100','Very walkable'],
                ['Schools','9 within 3km','GEMS, Repton, Cranleigh'],
                ['Transit','Metro 0.6km','Marina Walk station'],
                ['Beach','280m','Public beach access'],
              ].map(([k,v,sub])=>(
                <div key={k} className="glass-flat" style={{padding:14}}>
                  <div className="eyebrow">{k}</div>
                  <div style={{fontSize:18,fontWeight:700,fontFamily:'var(--scp-font-mono)'}}>{v}</div>
                  <div style={{fontSize:11,color:'#94a3b8',marginTop:4}}>{sub}</div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Side column */}
        <div style={{display:'flex',flexDirection:'column',gap:14}}>
          <div className="glass" style={{padding:18}}>
            <div style={{display:'flex',gap:12,alignItems:'center',marginBottom:14}}>
              <div className={`avatar ${agent.color}`} style={{width:44,height:44,fontSize:14}}>{agent.initials}</div>
              <div>
                <div style={{fontSize:14,fontWeight:700}}>{agent.name}</div>
                <div style={{fontSize:11,color:'#94a3b8'}}>{agent.role}</div>
                <div style={{fontSize:11,color:'#fbbf24',marginTop:2,display:'flex',alignItems:'center',gap:4}}>
                  <Icon name="star" size={11}/> {agent.rating} · {agent.deals} deals
                </div>
              </div>
            </div>
            <button className="btn btn-primary" style={{width:'100%',justifyContent:'center',marginBottom:8}}>
              Schedule viewing
            </button>
            <button className="btn" style={{width:'100%',justifyContent:'center',marginBottom:8}} onClick={onOpenChat}>
              <Icon name="sparkles" size={14}/> Ask AI about this listing
            </button>
            <button className="btn btn-ghost" style={{width:'100%',justifyContent:'center'}}>
              <Icon name="phone" size={14}/> Call agent
            </button>
          </div>

          <div className="glass" style={{padding:18}}>
            <h3 className="eyebrow">Mortgage estimate</h3>
            <div style={{fontSize:24,fontWeight:700,fontFamily:'var(--scp-font-mono)',marginBottom:4}}>
              AED {Math.round(prop.price * 0.005).toLocaleString()}<span style={{fontSize:12,color:'#94a3b8'}}>/mo</span>
            </div>
            <div style={{fontSize:11,color:'#94a3b8',marginBottom:12}}>20% down · 25y · 4.5% fixed · ENBD</div>
            <button className="btn btn-ghost" style={{width:'100%',justifyContent:'center'}}>
              Get pre-approved
            </button>
          </div>

          <div className="glass" style={{padding:18}}>
            <h3 className="eyebrow">Workflow status</h3>
            {[
              ['Disclosure pack','auto-generated', 'check'],
              ['NOC application','pending','clock'],
              ['Bank pre-approval','not started','plus'],
            ].map(([k,v,ic],i)=>(
              <div key={i} style={{display:'flex',gap:10,padding:'10px 0',
                borderBottom:i<2?'1px solid rgba(255,255,255,0.06)':'none',alignItems:'center'}}>
                <div style={{width:26,height:26,borderRadius:7,
                  background: v==='auto-generated'?'rgba(74,222,128,0.12)':v==='pending'?'rgba(251,191,36,0.12)':'rgba(255,255,255,0.04)',
                  border: `1px solid ${v==='auto-generated'?'rgba(74,222,128,0.30)':v==='pending'?'rgba(251,191,36,0.30)':'rgba(255,255,255,0.08)'}`,
                  display:'flex',alignItems:'center',justifyContent:'center',
                  color: v==='auto-generated'?'#4ade80':v==='pending'?'#fbbf24':'#94a3b8'}}>
                  <Icon name={ic} size={12}/>
                </div>
                <div style={{flex:1}}>
                  <div style={{fontSize:12,fontWeight:600}}>{k}</div>
                  <div style={{fontSize:10,color:'#94a3b8',textTransform:'uppercase',letterSpacing:0.4}}>{v}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </>
  );
}

function ValStat({ label, value, delta, pos }) {
  return (
    <div>
      <div style={{fontSize:10,color:'#94a3b8',fontWeight:700,textTransform:'uppercase',letterSpacing:0.55,marginBottom:4}}>{label}</div>
      <div style={{fontSize:20,fontWeight:700,fontFamily:'var(--scp-font-mono)',letterSpacing:-0.3}}>{value}</div>
      <div style={{fontSize:11,fontFamily:'var(--scp-font-mono)',marginTop:2,
        color:pos?'#4ade80':delta==='benchmark'?'#94a3b8':'#f87171'}}>{delta}</div>
    </div>
  );
}

// ============ AI CHAT ============
function ChatScreen({ contextProp, onOpenProperty }) {
  const seed = contextProp
    ? [
        { who:'ai', text:`Hi — I see you're looking at ${contextProp.title}. I can answer questions about the property, comps, mortgage, or schedule a viewing. What would help?`, ts:'now' },
      ]
    : [
        { who:'ai', text:`Hi — I'm Sceptre, your real-estate copilot. Tell me what you're after — emirate, budget, lifestyle, anything — and I'll surface listings that match. I can also handle valuations, viewings and paperwork.`, ts:'now' },
      ];
  const [messages, setMessages] = React.useState(seed);
  const [input, setInput] = React.useState('');
  const [typing, setTyping] = React.useState(false);
  const scrollRef = React.useRef();

  React.useEffect(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [messages, typing]);

  const send = async (text) => {
    if (!text.trim()) return;
    const userMsg = { who:'user', text, ts:'now' };
    const history = [...messages, userMsg];
    setMessages(m => [...m, userMsg]);
    setInput('');
    setTyping(true);

    try {
      const reply = await askClaude(text, contextProp, messages);
      setTyping(false);
      setMessages(m => [...m, reply]);
    } catch (err) {
      // Fallback to scripted reply if Claude is unavailable
      setTyping(false);
      setMessages(m => [...m, generateReply(text, contextProp)]);
    }
  };

  const suggestions = contextProp
    ? ['Is this priced fairly?','Show me 3 similar listings','What\'s the rental yield?','Schedule a viewing']
    : ['Sea view 3BR under 5M','Best value in Saadiyat','Compare Marina vs Downtown','Help me start a search'];

  return (
    <div style={{display:'flex',flexDirection:'column',height:'100%',maxHeight:'100%'}}>
      <div style={{display:'flex',alignItems:'center',gap:14,marginBottom:14,paddingBottom:14,borderBottom:'1px solid rgba(255,255,255,0.06)'}}>
        <div style={{width:44,height:44,borderRadius:12,background:'linear-gradient(135deg,#5eead4,#22d3ee,#0891b2)',
          display:'flex',alignItems:'center',justifyContent:'center',
          boxShadow:'0 0 20px rgba(34,211,238,0.4), inset 0 0.5px 0 rgba(255,255,255,0.4)'}}>
          <Icon name="sparkles" size={20} stroke={2}/>
        </div>
        <div style={{flex:1}}>
          <h1 style={{margin:0,fontSize:18,fontWeight:700}}>Sceptre Agent</h1>
          <div style={{fontSize:12,color:'#94a3b8',display:'flex',alignItems:'center',gap:6}}>
            <span className="status-dot pulse"/> Online · context-aware
            {contextProp && <> · viewing <span className="mono" style={{color:'#22d3ee'}}>{contextProp.id}</span></>}
          </div>
        </div>
        <button className="btn btn-ghost btn-icon"><Icon name="cog" size={15}/></button>
      </div>

      {/* Messages */}
      <div ref={scrollRef} style={{flex:1,overflow:'auto',display:'flex',flexDirection:'column',gap:12,padding:'8px 4px'}}>
        {messages.map((m, i) => (
          <ChatMessage key={i} msg={m} onOpenProperty={onOpenProperty}/>
        ))}
        {typing && (
          <div className="bubble bubble-ai" style={{alignSelf:'flex-start'}}>
            <div className="typing-dots"><span/><span/><span/></div>
          </div>
        )}
      </div>

      {/* Suggestions */}
      <div style={{display:'flex',gap:8,flexWrap:'wrap',padding:'14px 4px 10px'}}>
        {suggestions.map(s => (
          <button key={s} onClick={()=>send(s)} className="chip"
            style={{cursor:'pointer',padding:'6px 12px',fontSize:12,
              background:'rgba(34,211,238,0.06)',borderColor:'rgba(34,211,238,0.20)'}}>
            {s}
          </button>
        ))}
      </div>

      {/* Input */}
      <form onSubmit={e=>{e.preventDefault();send(input);}}
        style={{display:'flex',gap:10,padding:'10px',background:'rgba(0,0,0,0.3)',
          borderRadius:14,border:'1px solid rgba(255,255,255,0.10)',
          boxShadow:'inset 0 0.5px 0 rgba(255,255,255,0.06)'}}>
        <input value={input} onChange={e=>setInput(e.target.value)}
          placeholder="Ask anything about UAE properties…"
          style={{flex:1,padding:'10px 12px',border:'none',background:'transparent',color:'#f8fafc',
            fontSize:14,outline:'none',fontFamily:'inherit'}}/>
        <button type="submit" className="btn btn-primary" disabled={!input.trim()}>
          <Icon name="send" size={14}/> Send
        </button>
      </form>
    </div>
  );
}

function ChatMessage({ msg, onOpenProperty }) {
  if (msg.who === 'user') {
    return <div style={{display:'flex',justifyContent:'flex-end'}}>
      <div className="bubble bubble-user">{msg.text}</div>
    </div>;
  }
  return (
    <div style={{display:'flex',gap:10,alignItems:'flex-start'}}>
      <div style={{width:28,height:28,borderRadius:8,flexShrink:0,
        background:'linear-gradient(135deg,#5eead4,#22d3ee,#0891b2)',
        display:'flex',alignItems:'center',justifyContent:'center',
        boxShadow:'0 0 12px rgba(34,211,238,0.3)'}}>
        <Icon name="sparkles" size={14} stroke={2}/>
      </div>
      <div style={{flex:1,maxWidth:'85%'}}>
        <div className="bubble bubble-ai">{msg.text}</div>
        {msg.cards && (
          <div style={{display:'flex',gap:10,marginTop:10,flexWrap:'wrap'}}>
            {msg.cards.map(p=>(
              <div key={p.id} className="glass" style={{padding:10,width:200,cursor:'pointer'}} onClick={()=>onOpenProperty(p)}>
                <div className={`prop-img ${p.img}`} style={{height:80,marginBottom:8,borderRadius:8}}>
                  <ArchLines variant={1}/>
                </div>
                <div style={{fontSize:12,fontWeight:700,marginBottom:2,whiteSpace:'nowrap',overflow:'hidden',textOverflow:'ellipsis'}}>{p.title}</div>
                <div style={{fontSize:11,color:'#22d3ee',fontFamily:'var(--scp-font-mono)',fontWeight:700}}>{fmtAEDShort(p.price)}</div>
                <div style={{fontSize:10,color:'#94a3b8',marginTop:2}}>{p.area}</div>
              </div>
            ))}
          </div>
        )}
        {msg.actions && (
          <div style={{display:'flex',gap:8,marginTop:8,flexWrap:'wrap'}}>
            {msg.actions.map(a => (
              <button key={a} className="chip" style={{cursor:'pointer',padding:'5px 11px',background:'rgba(255,255,255,0.05)'}}>
                {a}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// ============ Claude-powered chat ============
async function askClaude(userText, ctx, history) {
  const catalog = window.PROPERTIES.map(p => ({
    id: p.id, title: p.title, area: p.area, price: p.price,
    beds: p.beds, baths: p.baths, sqft: p.sqft, type: p.type,
    features: p.features, match: p.match,
  }));

  const sysCtx = ctx
    ? `\nThe user is currently viewing this listing:\n${JSON.stringify({id:ctx.id,title:ctx.title,area:ctx.area,price:ctx.price,beds:ctx.beds,baths:ctx.baths,sqft:ctx.sqft,features:ctx.features},null,2)}\n`
    : '';

  const system = `You are Sceptre, a UAE real-estate copilot helping a homebuyer/seller. Be concise, warm, and concrete. Prices in AED. You know UAE markets — Dubai (Marina, Downtown, Palm, JBR, Business Bay), Abu Dhabi (Saadiyat, Al Reem, Yas), Sharjah, RAK. Speak like a senior agent who's done a thousand deals — direct, occasionally opinionated, never salesy.
${sysCtx}
Available listings the user can browse:
${JSON.stringify(catalog,null,2)}

You MUST reply with valid JSON only, in this exact shape:
{
  "text": "your reply, 1-3 short paragraphs, no markdown",
  "cardIds": ["P-1042"],   // optional, 1-3 listing IDs from the catalog if you want to surface them
  "actions": ["Schedule viewing","Run valuation"]   // optional, 2-4 short action chips (max 22 chars each)
}

Rules:
- Only include cardIds when surfacing properties is genuinely helpful (e.g. "show me", "compare", "find").
- Only include actions when there's a clear next step.
- Never invent listing IDs — only use IDs from the catalog above.
- Never wrap the JSON in code fences. Plain JSON only.`;

  const recentHistory = history.slice(-6).map(m => ({
    role: m.who === 'user' ? 'user' : 'assistant',
    content: m.text || '(showed property cards)',
  }));

  const resp = await window.claude.complete({
    system,
    messages: [...recentHistory, { role:'user', content: userText }],
  });

  // Parse JSON response
  let parsed;
  try {
    const cleaned = resp.replace(/^```json\s*|\s*```$/g, '').trim();
    parsed = JSON.parse(cleaned);
  } catch {
    return { who:'ai', text: resp.slice(0, 600) };
  }

  const cards = (parsed.cardIds || [])
    .map(id => window.PROPERTIES.find(p => p.id === id))
    .filter(Boolean)
    .slice(0, 3);

  return {
    who: 'ai',
    text: parsed.text || 'Let me think about that.',
    cards: cards.length ? cards : undefined,
    actions: parsed.actions && parsed.actions.length ? parsed.actions.slice(0,4) : undefined,
  };
}

function generateReply(text, ctx) {
  const t = text.toLowerCase();
  if (t.includes('similar') || t.includes('compare') || t.includes('show me')) {
    const cards = window.PROPERTIES.slice(0,3);
    return { who:'ai', text:'Here are three matches I think you\'ll like — all within 15% of your stated criteria:', cards };
  }
  if (t.includes('priced') || t.includes('value') || t.includes('worth')) {
    return { who:'ai', text:`Yes — based on 14 comps in ${ctx?ctx.area:'the area'}, this listing is ~2% below my model estimate. Sellers in this micro-market have been firm, so an offer 1-3% under list is typical. I'd open at AED ${ctx?Math.round(ctx.price*0.97/1e6*100)/100:8.1}M.`, actions:['Run full valuation','See comparables'] };
  }
  if (t.includes('yield') || t.includes('rent')) {
    return { who:'ai', text:'Based on current rental data for the area, expected gross yield is 5.8-6.4%. After service charges, DEWA and management, net yield lands around 4.6%. Marina and JBR have historically been the strongest cash-flow spots in Dubai.' };
  }
  if (t.includes('viewing') || t.includes('schedule')) {
    return { who:'ai', text:'I can book you in. The next 3 available slots are tomorrow 10:30, tomorrow 16:00, and Friday 11:00. Layla can host all three. Which works?', actions:['Tomorrow 10:30','Tomorrow 16:00','Friday 11:00'] };
  }
  if (t.includes('mortgage') || t.includes('pre-approved') || t.includes('approval')) {
    return { who:'ai', text:'I\'ll prep your mortgage pack. ENBD, Mashreq and FAB are currently quoting 4.3-4.7% on a 25y fixed. I\'ll need salary cert, 6mo bank statements and ID — can pull these from your wallet if you\'ve uploaded them.', actions:['Use saved docs','Upload now'] };
  }
  if (t.includes('marina') || t.includes('downtown') || t.includes('saadiyat')) {
    const cards = window.PROPERTIES.slice(0,3);
    return { who:'ai', text:'Got it — here\'s what stands out in that area right now. Match scores reflect your saved preferences (sea view, smart home, 3BR+).', cards };
  }
  return { who:'ai', text:'Got it. I\'m pulling matching listings now — give me a moment to scan the live market.', cards: window.PROPERTIES.slice(2,5) };
}

Object.assign(window, { BrowseScreen, PropertyDetailScreen, ChatScreen, askClaude });
