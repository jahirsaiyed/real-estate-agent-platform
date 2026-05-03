// Mobile companion — buyer-side iOS app
// Hosted inside an iOS frame on the design canvas

const { Icon: MIcon, ArchLines: MArchLines, fmtAEDShort: mFmt } = window;

function MobileApp() {
  const [tab, setTab] = React.useState('home');
  const [detailProp, setDetailProp] = React.useState(null);

  return (
    <div style={{height:'100%',display:'flex',flexDirection:'column',
      background:'linear-gradient(180deg, #0a0d18 0%, #131829 60%, #0a0d18 100%)',
      color:'#f8fafc',fontFamily:'var(--scp-font-sans)',position:'relative'}}>
      {/* ambient orb */}
      <div style={{position:'absolute',top:-60,right:-60,width:200,height:200,borderRadius:'50%',
        background:'radial-gradient(circle,rgba(34,211,238,0.20),transparent 70%)',pointerEvents:'none'}}/>
      <div style={{position:'absolute',bottom:60,left:-40,width:180,height:180,borderRadius:'50%',
        background:'radial-gradient(circle,rgba(167,139,250,0.18),transparent 70%)',pointerEvents:'none'}}/>

      <div style={{flex:1,overflow:'auto',position:'relative',zIndex:1,paddingTop:54,paddingBottom:80}}>
        {detailProp ? (
          <MPropertyDetail prop={detailProp} onBack={()=>setDetailProp(null)}/>
        ) : tab==='home' ? (
          <MHome onOpenProp={setDetailProp}/>
        ) : tab==='search' ? (
          <MSearch onOpenProp={setDetailProp}/>
        ) : tab==='offers' ? (
          <MOffers/>
        ) : tab==='chat' ? (
          <MChat onOpenProp={setDetailProp}/>
        ) : null}
      </div>

      {/* Bottom tab bar */}
      <div style={{position:'absolute',bottom:18,left:14,right:14,zIndex:10,
        background:'rgba(20,24,40,0.7)',backdropFilter:'blur(28px) saturate(140%)',
        WebkitBackdropFilter:'blur(28px) saturate(140%)',
        borderRadius:24,padding:'10px 6px',display:'flex',justifyContent:'space-around',
        border:'1px solid rgba(255,255,255,0.10)',
        boxShadow:'0 12px 40px rgba(0,0,0,0.45), inset 0 0.5px 0 rgba(255,255,255,0.10)'}}>
        {[
          {k:'home',i:'home',l:'Home'},
          {k:'search',i:'search',l:'Search'},
          {k:'chat',i:'sparkles',l:'AI'},
          {k:'offers',i:'handshake',l:'Offers'},
        ].map(t => (
          <button key={t.k} onClick={()=>{setTab(t.k);setDetailProp(null);}}
            style={{flex:1,background:'none',border:'none',padding:'4px 8px',cursor:'pointer',
              display:'flex',flexDirection:'column',alignItems:'center',gap:2,
              color: tab===t.k && !detailProp ? '#22d3ee' : '#94a3b8'}}>
            <MIcon name={t.i} size={18}/>
            <span style={{fontSize:9,fontWeight:600,letterSpacing:0.2}}>{t.l}</span>
          </button>
        ))}
      </div>
    </div>
  );
}

// ============ HOME ============
function MHome({ onOpenProp }) {
  const featured = window.PROPERTIES[0];
  const saved = window.PROPERTIES.slice(1,4);
  return (
    <div style={{padding:'8px 18px 24px'}}>
      <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:14}}>
        <div>
          <div style={{fontSize:11,color:'#94a3b8',fontWeight:600}}>Sunday, 3 May</div>
          <div style={{fontSize:20,fontWeight:700,letterSpacing:-0.3,marginTop:2}}>Welcome, Layla</div>
        </div>
        <div style={{width:36,height:36,borderRadius:'50%',
          background:'linear-gradient(135deg,#5eead4,#22d3ee)',
          display:'flex',alignItems:'center',justifyContent:'center',
          fontSize:11,fontWeight:700,color:'#0a0d18',
          boxShadow:'0 0 14px rgba(34,211,238,0.35)'}}>LR</div>
      </div>

      {/* AI nudge banner */}
      <div onClick={()=>onOpenProp(featured)}
        style={{borderRadius:18,overflow:'hidden',marginBottom:16,cursor:'pointer',
          border:'1px solid rgba(34,211,238,0.35)',
          background:'linear-gradient(135deg,rgba(34,211,238,0.16),rgba(94,234,212,0.06) 60%,rgba(0,0,0,0.3))',
          boxShadow:'0 8px 24px rgba(34,211,238,0.18), inset 0 0.5px 0 rgba(255,255,255,0.10)'}}>
        <div style={{padding:'14px 16px'}}>
          <div style={{display:'flex',alignItems:'center',gap:6,marginBottom:8}}>
            <MIcon name="sparkles" size={13}/>
            <span style={{fontSize:10,fontWeight:700,letterSpacing:0.4,textTransform:'uppercase',color:'#22d3ee'}}>From Sceptre</span>
          </div>
          <div style={{fontSize:13,lineHeight:1.45,color:'#f8fafc'}}>
            The seller of <strong style={{color:'#5eead4'}}>Marina Penthouse</strong> countered at AED 8.2M.
            Comps support <strong>8.05M</strong> as your walk-up.
          </div>
          <div style={{display:'flex',gap:8,marginTop:10}}>
            <button style={{flex:1,padding:'7px 10px',borderRadius:10,fontSize:11,fontWeight:600,
              background:'#22d3ee',color:'#0a0d18',border:'none'}}>Counter at 8.05M</button>
            <button style={{padding:'7px 10px',borderRadius:10,fontSize:11,fontWeight:600,
              background:'rgba(255,255,255,0.08)',color:'#f8fafc',border:'1px solid rgba(255,255,255,0.12)'}}>Discuss</button>
          </div>
        </div>
      </div>

      {/* Active offer card */}
      <div style={{marginBottom:18}}>
        <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:8}}>
          <span style={{fontSize:10,fontWeight:700,letterSpacing:0.55,textTransform:'uppercase',color:'#94a3b8'}}>Active offer</span>
          <span style={{fontSize:10,color:'#fbbf24',fontWeight:700}}>● Countered</span>
        </div>
        <div style={{padding:'12px',borderRadius:14,background:'rgba(255,255,255,0.04)',
          border:'1px solid rgba(255,255,255,0.08)'}}>
          <div style={{display:'flex',gap:10,alignItems:'center'}}>
            <div className="prop-img img-1" style={{width:54,height:54,borderRadius:12,marginBottom:0,position:'relative',overflow:'hidden'}}>
              <MArchLines variant={1}/>
            </div>
            <div style={{flex:1,minWidth:0}}>
              <div style={{fontSize:13,fontWeight:700,whiteSpace:'nowrap',overflow:'hidden',textOverflow:'ellipsis'}}>Marina Penthouse</div>
              <div style={{fontSize:11,color:'#94a3b8'}}>Dubai Marina · 3BR · 3,210 sqft</div>
            </div>
          </div>
          <div style={{display:'grid',gridTemplateColumns:'1fr 1fr 1fr',gap:6,marginTop:12,fontFamily:'var(--scp-font-mono)'}}>
            <div><div style={{fontSize:9,color:'#94a3b8',textTransform:'uppercase',letterSpacing:0.4,fontWeight:700}}>List</div>
              <div style={{fontSize:12,color:'#cbd5e1',fontWeight:700,marginTop:2}}>8.4M</div></div>
            <div><div style={{fontSize:9,color:'#22d3ee',textTransform:'uppercase',letterSpacing:0.4,fontWeight:700}}>You</div>
              <div style={{fontSize:12,color:'#22d3ee',fontWeight:700,marginTop:2}}>7.95M</div></div>
            <div><div style={{fontSize:9,color:'#fbbf24',textTransform:'uppercase',letterSpacing:0.4,fontWeight:700}}>Counter</div>
              <div style={{fontSize:12,color:'#fbbf24',fontWeight:700,marginTop:2}}>8.2M</div></div>
          </div>
        </div>
      </div>

      {/* Saved homes */}
      <div style={{display:'flex',justifyContent:'space-between',alignItems:'baseline',marginBottom:10}}>
        <span style={{fontSize:10,fontWeight:700,letterSpacing:0.55,textTransform:'uppercase',color:'#94a3b8'}}>Saved homes</span>
        <span style={{fontSize:11,color:'#22d3ee',fontWeight:600}}>See all</span>
      </div>
      <div style={{display:'grid',gap:10}}>
        {saved.map(p => (
          <div key={p.id} onClick={()=>onOpenProp(p)}
            style={{display:'flex',gap:10,padding:10,borderRadius:14,
              background:'rgba(255,255,255,0.03)',border:'1px solid rgba(255,255,255,0.06)',
              cursor:'pointer'}}>
            <div className={`prop-img ${p.img}`} style={{width:64,height:64,borderRadius:10,marginBottom:0,position:'relative',overflow:'hidden',flexShrink:0}}>
              <MArchLines variant={(p.id.charCodeAt(2))%3+1}/>
            </div>
            <div style={{flex:1,minWidth:0}}>
              <div style={{display:'flex',justifyContent:'space-between',alignItems:'baseline'}}>
                <span style={{fontSize:13,fontWeight:700,whiteSpace:'nowrap',overflow:'hidden',textOverflow:'ellipsis',maxWidth:140}}>{p.title}</span>
                <span style={{fontSize:10,color:'#22d3ee',fontFamily:'var(--scp-font-mono)',fontWeight:700,flexShrink:0,marginLeft:6}}>{p.match}%</span>
              </div>
              <div style={{fontSize:11,color:'#94a3b8',marginTop:2}}>{p.area}</div>
              <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginTop:6}}>
                <span style={{fontSize:12,color:'#5eead4',fontFamily:'var(--scp-font-mono)',fontWeight:700}}>{mFmt(p.price)}</span>
                <span style={{fontSize:9,color:'#4ade80',fontWeight:700}}>● ALERT ON</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ============ SEARCH ============
function MSearch({ onOpenProp }) {
  return (
    <div style={{padding:'8px 18px 24px'}}>
      <div style={{fontSize:22,fontWeight:700,letterSpacing:-0.3,marginBottom:14}}>Find a home</div>

      <div style={{display:'flex',alignItems:'center',gap:8,padding:'10px 14px',borderRadius:14,
        background:'rgba(0,0,0,0.3)',border:'1px solid rgba(255,255,255,0.10)',marginBottom:12}}>
        <MIcon name="search" size={15}/>
        <span style={{fontSize:13,color:'#94a3b8'}}>Marina, sea view, 3BR…</span>
      </div>

      <div style={{display:'flex',gap:6,marginBottom:14,overflow:'auto',paddingBottom:4}}>
        {['All','Apartments','Villas','Penthouses','Townhouses'].map((c,i)=>(
          <span key={c} style={{padding:'5px 11px',borderRadius:999,fontSize:11,fontWeight:600,whiteSpace:'nowrap',
            background:i===0?'rgba(34,211,238,0.16)':'rgba(255,255,255,0.04)',
            color:i===0?'#22d3ee':'#94a3b8',
            border:`1px solid ${i===0?'rgba(34,211,238,0.30)':'rgba(255,255,255,0.08)'}`}}>{c}</span>
        ))}
      </div>

      <div style={{display:'flex',justifyContent:'space-between',alignItems:'baseline',marginBottom:10}}>
        <span style={{fontSize:11,color:'#94a3b8'}}>{window.PROPERTIES.length} homes · sorted by AI match</span>
        <span style={{fontSize:11,color:'#22d3ee',fontWeight:600}}>Sort</span>
      </div>

      <div style={{display:'grid',gap:12}}>
        {window.PROPERTIES.slice(0,5).map((p,i) => (
          <div key={p.id} onClick={()=>onOpenProp(p)}
            style={{borderRadius:16,overflow:'hidden',
              background:'rgba(255,255,255,0.03)',border:'1px solid rgba(255,255,255,0.06)',
              cursor:'pointer'}}>
            <div className={`prop-img ${p.img}`} style={{height:130,marginBottom:0,position:'relative',overflow:'hidden',borderRadius:'16px 16px 0 0'}}>
              <MArchLines variant={(i%3)+1}/>
              <div style={{position:'absolute',top:10,left:10,
                padding:'4px 9px',borderRadius:999,fontSize:10,fontWeight:700,
                background:'rgba(34,211,238,0.92)',color:'#0a0d18',
                boxShadow:'0 0 14px rgba(34,211,238,0.40)'}}>{p.match}% match</div>
              <div style={{position:'absolute',top:10,right:10,
                width:30,height:30,borderRadius:'50%',
                background:'rgba(20,24,40,0.7)',backdropFilter:'blur(8px)',
                display:'flex',alignItems:'center',justifyContent:'center',
                color:i===0?'#f87171':'#94a3b8'}}>
                <MIcon name="heart" size={13} stroke={2}/>
              </div>
            </div>
            <div style={{padding:'10px 12px 12px'}}>
              <div style={{display:'flex',justifyContent:'space-between',alignItems:'baseline'}}>
                <span style={{fontSize:14,fontWeight:700,whiteSpace:'nowrap',overflow:'hidden',textOverflow:'ellipsis',maxWidth:170}}>{p.title}</span>
                <span style={{fontSize:13,color:'#5eead4',fontFamily:'var(--scp-font-mono)',fontWeight:700}}>{mFmt(p.price)}</span>
              </div>
              <div style={{fontSize:11,color:'#94a3b8',marginTop:2}}>{p.area}</div>
              <div style={{display:'flex',gap:10,marginTop:8,fontSize:10,color:'#cbd5e1',fontFamily:'var(--scp-font-mono)'}}>
                <span>{p.beds} BD</span>
                <span>{p.baths} BA</span>
                <span>{p.sqft.toLocaleString()} ft²</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ============ PROPERTY DETAIL ============
function MPropertyDetail({ prop, onBack }) {
  return (
    <div>
      <div className={`prop-img ${prop.img}`} style={{height:240,marginBottom:0,position:'relative',overflow:'hidden',borderRadius:0}}>
        <MArchLines variant={1}/>
        <button onClick={onBack} style={{position:'absolute',top:14,left:14,
          width:36,height:36,borderRadius:'50%',
          background:'rgba(20,24,40,0.7)',backdropFilter:'blur(8px)',
          border:'1px solid rgba(255,255,255,0.12)',color:'#f8fafc',cursor:'pointer',
          display:'flex',alignItems:'center',justifyContent:'center'}}>
          <MIcon name="chevL" size={16}/>
        </button>
        <button style={{position:'absolute',top:14,right:14,
          width:36,height:36,borderRadius:'50%',
          background:'rgba(20,24,40,0.7)',backdropFilter:'blur(8px)',
          border:'1px solid rgba(255,255,255,0.12)',color:'#f87171',cursor:'pointer',
          display:'flex',alignItems:'center',justifyContent:'center'}}>
          <MIcon name="heart" size={15} stroke={2}/>
        </button>
        {/* image dots */}
        <div style={{position:'absolute',bottom:12,left:'50%',transform:'translateX(-50%)',
          display:'flex',gap:5}}>
          {[0,1,2,3,4].map(i=>(
            <div key={i} style={{width:i===0?16:5,height:5,borderRadius:3,
              background:i===0?'#22d3ee':'rgba(255,255,255,0.45)',transition:'width 0.2s'}}/>
          ))}
        </div>
      </div>

      <div style={{padding:'18px 18px 8px'}}>
        <div style={{display:'flex',justifyContent:'space-between',alignItems:'flex-start',gap:10}}>
          <div style={{flex:1}}>
            <div style={{fontSize:11,color:'#94a3b8',fontWeight:600}}>{prop.area} · {prop.emirate}</div>
            <div style={{fontSize:20,fontWeight:700,letterSpacing:-0.3,marginTop:3,lineHeight:1.2}}>{prop.title}</div>
          </div>
          <div style={{padding:'5px 10px',borderRadius:999,fontSize:11,fontWeight:700,
            background:'rgba(34,211,238,0.16)',color:'#22d3ee',
            border:'1px solid rgba(34,211,238,0.30)'}}>{prop.match}% match</div>
        </div>

        <div style={{fontSize:24,fontWeight:700,fontFamily:'var(--scp-font-mono)',color:'#5eead4',marginTop:10}}>
          {mFmt(prop.price)}
          <span style={{fontSize:11,color:'#4ade80',marginLeft:8,fontWeight:600,fontFamily:'var(--scp-font-sans)'}}>{prop.trend}</span>
        </div>

        <div style={{display:'flex',justifyContent:'space-between',marginTop:14,padding:'12px 14px',
          borderRadius:14,background:'rgba(255,255,255,0.04)',
          border:'1px solid rgba(255,255,255,0.06)',fontFamily:'var(--scp-font-mono)'}}>
          {[
            {l:'Beds',v:prop.beds},
            {l:'Baths',v:prop.baths},
            {l:'Sqft',v:prop.sqft.toLocaleString()},
            {l:'Type',v:prop.type},
          ].map(s=>(
            <div key={s.l} style={{textAlign:'center'}}>
              <div style={{fontSize:9,color:'#94a3b8',letterSpacing:0.4,textTransform:'uppercase',fontWeight:700}}>{s.l}</div>
              <div style={{fontSize:13,color:'#f8fafc',fontWeight:700,marginTop:3,fontFamily:'var(--scp-font-sans)'}}>{s.v}</div>
            </div>
          ))}
        </div>

        {/* AI valuation card */}
        <div style={{marginTop:14,borderRadius:14,padding:14,
          background:'linear-gradient(135deg,rgba(34,211,238,0.10),rgba(94,234,212,0.04))',
          border:'1px solid rgba(34,211,238,0.25)'}}>
          <div style={{display:'flex',alignItems:'center',gap:6,marginBottom:8}}>
            <MIcon name="sparkles" size={13}/>
            <span style={{fontSize:10,fontWeight:700,letterSpacing:0.55,textTransform:'uppercase',color:'#22d3ee'}}>Sceptre valuation</span>
          </div>
          <div style={{fontSize:12,lineHeight:1.55,color:'#cbd5e1'}}>
            Based on 14 comparable sales in {prop.area}, this listing is <strong style={{color:'#5eead4'}}>~2% below</strong> my model estimate.
            I'd open at <strong style={{color:'#5eead4'}}>AED {(prop.price*0.97/1e6).toFixed(2)}M</strong>.
          </div>
          <div style={{display:'flex',gap:8,marginTop:12}}>
            <button style={{flex:1,padding:'9px 10px',borderRadius:10,fontSize:11,fontWeight:700,
              background:'#22d3ee',color:'#0a0d18',border:'none',
              boxShadow:'0 0 14px rgba(34,211,238,0.30)'}}>Make offer</button>
            <button style={{flex:1,padding:'9px 10px',borderRadius:10,fontSize:11,fontWeight:600,
              background:'rgba(255,255,255,0.06)',color:'#f8fafc',border:'1px solid rgba(255,255,255,0.10)'}}>
              <MIcon name="cal" size={12}/> Book viewing
            </button>
          </div>
        </div>

        {/* Features */}
        <div style={{marginTop:18,marginBottom:6}}>
          <div style={{fontSize:10,fontWeight:700,letterSpacing:0.55,textTransform:'uppercase',color:'#94a3b8',marginBottom:8}}>Features</div>
          <div style={{display:'flex',flexWrap:'wrap',gap:6}}>
            {prop.features.map(f => (
              <span key={f} style={{padding:'5px 10px',borderRadius:999,fontSize:11,fontWeight:600,
                background:'rgba(255,255,255,0.04)',color:'#cbd5e1',
                border:'1px solid rgba(255,255,255,0.08)'}}>{f}</span>
            ))}
          </div>
        </div>

        <p style={{fontSize:12,color:'#94a3b8',lineHeight:1.55,marginTop:14}}>
          {prop.desc}
        </p>
      </div>
    </div>
  );
}

// ============ OFFERS ============
function MOffers() {
  const offers = window.MY_OFFERS;
  const stages = window.OFFER_STAGES;
  return (
    <div style={{padding:'8px 18px 24px'}}>
      <div style={{fontSize:22,fontWeight:700,letterSpacing:-0.3,marginBottom:4}}>My offers</div>
      <div style={{fontSize:12,color:'#94a3b8',marginBottom:18}}>{offers.filter(o=>o.stage!=='accepted'&&o.stage!=='rejected').length} active</div>

      <div style={{display:'grid',gap:10}}>
        {offers.map(o => {
          const p = window.PROPERTIES.find(x=>x.id===o.propertyId) || {};
          const stage = stages.find(s=>s.key===o.stage) || stages[0];
          const delta = ((o.myOffer - o.listPrice) / o.listPrice * 100);
          return (
            <div key={o.id} style={{padding:14,borderRadius:14,
              background:'rgba(255,255,255,0.03)',border:'1px solid rgba(255,255,255,0.06)',
              borderLeft:`3px solid ${stage.accent}`}}>
              <div style={{display:'flex',justifyContent:'space-between',alignItems:'flex-start',gap:10}}>
                <div style={{display:'flex',gap:10,flex:1,minWidth:0}}>
                  <div className={`prop-img ${p.img||'img-1'}`} style={{width:46,height:46,borderRadius:10,marginBottom:0,flexShrink:0,position:'relative',overflow:'hidden'}}>
                    <MArchLines variant={1}/>
                  </div>
                  <div style={{flex:1,minWidth:0}}>
                    <div style={{fontSize:13,fontWeight:700,whiteSpace:'nowrap',overflow:'hidden',textOverflow:'ellipsis'}}>{p.title}</div>
                    <div style={{fontSize:10,color:'#94a3b8',marginTop:2}}>{p.area}</div>
                  </div>
                </div>
                <span style={{padding:'3px 9px',borderRadius:999,fontSize:9,fontWeight:700,
                  textTransform:'uppercase',letterSpacing:0.45,
                  background:stage.accent+'1e',color:stage.accent,border:`1px solid ${stage.accent}55`,whiteSpace:'nowrap'}}>
                  {stage.label}
                </span>
              </div>
              <div style={{display:'grid',gridTemplateColumns:o.counter?'1fr 1fr 1fr':'1fr 1fr',gap:8,marginTop:12,
                padding:'10px',background:'rgba(0,0,0,0.25)',borderRadius:10,fontFamily:'var(--scp-font-mono)'}}>
                <div><div style={{fontSize:9,color:'#94a3b8',letterSpacing:0.4,textTransform:'uppercase',fontWeight:700}}>List</div>
                  <div style={{fontSize:11,color:'#cbd5e1',fontWeight:700,marginTop:2}}>{mFmt(o.listPrice)}</div></div>
                <div><div style={{fontSize:9,color:'#22d3ee',letterSpacing:0.4,textTransform:'uppercase',fontWeight:700}}>You</div>
                  <div style={{fontSize:11,color:'#22d3ee',fontWeight:700,marginTop:2}}>{mFmt(o.myOffer)}</div></div>
                {o.counter && (
                  <div><div style={{fontSize:9,color:'#fbbf24',letterSpacing:0.4,textTransform:'uppercase',fontWeight:700}}>Counter</div>
                    <div style={{fontSize:11,color:'#fbbf24',fontWeight:700,marginTop:2}}>{mFmt(o.counter)}</div></div>
                )}
              </div>
              <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginTop:10}}>
                <span style={{fontSize:10,color:'#64748b',fontFamily:'var(--scp-font-mono)'}}>{o.id} · {o.updated}</span>
                <span style={{fontSize:10,color:delta<-3?'#4ade80':delta<0?'#22d3ee':'#94a3b8',fontFamily:'var(--scp-font-mono)',fontWeight:700}}>
                  {delta>0?'+':''}{delta.toFixed(1)}% vs list
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ============ AI CHAT ============
function MChat({ onOpenProp }) {
  const [messages, setMessages] = React.useState([
    { who:'ai', text:'Hi — I\'m Sceptre, your real-estate copilot. Ask me anything about UAE properties, your offers, or this market.' },
    { who:'ai', text:'Three things on my radar for you today:' , chips:['Counter on Marina Penthouse','New Saadiyat match','ENBD rate dropped 0.15%']},
  ]);
  const [input, setInput] = React.useState('');
  const [typing, setTyping] = React.useState(false);

  const send = async (text) => {
    if (!text.trim()) return;
    setMessages(m=>[...m,{who:'user',text}]);
    setInput('');
    setTyping(true);
    try {
      const reply = await window.askClaude(text, null, messages);
      setTyping(false);
      setMessages(m=>[...m, reply]);
    } catch {
      setTyping(false);
      setMessages(m=>[...m, {who:'ai',text:'Got it — let me think on that.'}]);
    }
  };

  return (
    <div style={{padding:'8px 14px 4px',display:'flex',flexDirection:'column',height:'100%'}}>
      <div style={{display:'flex',alignItems:'center',gap:10,marginBottom:14,padding:'4px 4px'}}>
        <div style={{width:36,height:36,borderRadius:10,
          background:'linear-gradient(135deg,#5eead4,#22d3ee,#0891b2)',
          display:'flex',alignItems:'center',justifyContent:'center',
          boxShadow:'0 0 16px rgba(34,211,238,0.4)'}}>
          <MIcon name="sparkles" size={17} stroke={2}/>
        </div>
        <div>
          <div style={{fontSize:15,fontWeight:700}}>Sceptre Agent</div>
          <div style={{fontSize:10,color:'#94a3b8'}}>● online · powered by Claude</div>
        </div>
      </div>

      <div style={{flex:1,overflow:'auto',display:'flex',flexDirection:'column',gap:10,padding:'4px 4px'}}>
        {messages.map((m,i)=>(
          m.who==='user' ? (
            <div key={i} style={{alignSelf:'flex-end',maxWidth:'80%',padding:'9px 13px',borderRadius:'16px 16px 4px 16px',
              background:'linear-gradient(135deg,#22d3ee,#0891b2)',color:'#0a0d18',fontSize:12.5,fontWeight:600,lineHeight:1.4}}>
              {m.text}
            </div>
          ) : (
            <div key={i} style={{alignSelf:'flex-start',maxWidth:'82%'}}>
              <div style={{padding:'9px 13px',borderRadius:'16px 16px 16px 4px',
                background:'rgba(255,255,255,0.05)',color:'#f8fafc',fontSize:12.5,lineHeight:1.45,
                border:'1px solid rgba(255,255,255,0.08)'}}>
                {m.text}
              </div>
              {m.chips && (
                <div style={{display:'flex',gap:6,marginTop:8,flexWrap:'wrap'}}>
                  {m.chips.map(c => (
                    <button key={c} onClick={()=>send(c)} style={{padding:'5px 10px',borderRadius:999,fontSize:10.5,fontWeight:600,
                      background:'rgba(34,211,238,0.10)',color:'#22d3ee',
                      border:'1px solid rgba(34,211,238,0.25)',cursor:'pointer'}}>
                      {c}
                    </button>
                  ))}
                </div>
              )}
              {m.cards && (
                <div style={{display:'grid',gap:8,marginTop:8}}>
                  {m.cards.map(p => (
                    <div key={p.id} onClick={()=>onOpenProp(p)}
                      style={{display:'flex',gap:8,padding:8,borderRadius:12,
                        background:'rgba(255,255,255,0.03)',border:'1px solid rgba(255,255,255,0.06)',cursor:'pointer'}}>
                      <div className={`prop-img ${p.img}`} style={{width:48,height:48,borderRadius:8,marginBottom:0,flexShrink:0,position:'relative',overflow:'hidden'}}>
                        <MArchLines variant={1}/>
                      </div>
                      <div style={{flex:1,minWidth:0}}>
                        <div style={{fontSize:11,fontWeight:700,whiteSpace:'nowrap',overflow:'hidden',textOverflow:'ellipsis'}}>{p.title}</div>
                        <div style={{fontSize:10,color:'#22d3ee',fontFamily:'var(--scp-font-mono)',fontWeight:700,marginTop:2}}>{mFmt(p.price)}</div>
                        <div style={{fontSize:9,color:'#94a3b8',marginTop:1}}>{p.area}</div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )
        ))}
        {typing && (
          <div style={{alignSelf:'flex-start',padding:'9px 13px',borderRadius:'16px 16px 16px 4px',
            background:'rgba(255,255,255,0.05)',border:'1px solid rgba(255,255,255,0.08)'}}>
            <div className="typing-dots"><span/><span/><span/></div>
          </div>
        )}
      </div>

      <form onSubmit={e=>{e.preventDefault();send(input);}}
        style={{display:'flex',gap:6,marginTop:10,padding:6,
          background:'rgba(0,0,0,0.4)',borderRadius:18,
          border:'1px solid rgba(255,255,255,0.10)'}}>
        <input value={input} onChange={e=>setInput(e.target.value)}
          placeholder="Ask anything…"
          style={{flex:1,padding:'8px 12px',border:'none',background:'transparent',color:'#f8fafc',
            fontSize:13,outline:'none',fontFamily:'inherit'}}/>
        <button type="submit" disabled={!input.trim()} style={{padding:'8px 12px',borderRadius:14,
          background: input.trim()?'#22d3ee':'rgba(255,255,255,0.06)',
          color: input.trim()?'#0a0d18':'#94a3b8',
          border:'none',cursor:input.trim()?'pointer':'default'}}>
          <MIcon name="send" size={13}/>
        </button>
      </form>
    </div>
  );
}

Object.assign(window, { MobileApp });
