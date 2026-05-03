// Main app shell + router

const { Icon } = window;

const TWEAK_DEFAULTS = /*EDITMODE-BEGIN*/{
  "accentHue": "cyan",
  "browseView": "grid",
  "density": "comfortable",
  "showOrbs": true
}/*EDITMODE-END*/;

function App() {
  const [route, setRoute] = React.useState({ name:'browse' });
  const [tweaks, setTweak] = window.useTweaks(TWEAK_DEFAULTS);
  const [browseView, setBrowseView] = React.useState(tweaks.browseView || 'grid');

  // Apply accent hue tweak (recolors :root vars)
  React.useEffect(() => {
    const map = {
      cyan:   { accent:'#22d3ee', bright:'#5eead4', dim:'#0891b2', glow:'rgba(34,211,238,0.35)' },
      violet: { accent:'#a78bfa', bright:'#c4b5fd', dim:'#7c3aed', glow:'rgba(167,139,250,0.35)' },
      emerald:{ accent:'#34d399', bright:'#6ee7b7', dim:'#059669', glow:'rgba(52,211,153,0.35)' },
      amber:  { accent:'#fbbf24', bright:'#fde68a', dim:'#d97706', glow:'rgba(251,191,36,0.35)' },
    };
    const m = map[tweaks.accentHue] || map.cyan;
    document.documentElement.style.setProperty('--scp-accent', m.accent);
    document.documentElement.style.setProperty('--scp-accent-bright', m.bright);
    document.documentElement.style.setProperty('--scp-accent-dim', m.dim);
    document.documentElement.style.setProperty('--scp-accent-glow', m.glow);
  }, [tweaks.accentHue]);

  React.useEffect(() => {
    if (tweaks.browseView) setBrowseView(tweaks.browseView);
  }, [tweaks.browseView]);

  const goto = name => setRoute({ name });
  const openProperty = (prop) => setRoute({ name:'detail', prop });
  const openChat = (prop) => setRoute({ name:'chat', contextProp: prop });

  const navItems = [
    { key:'browse', label:'Find a Home', icon:'search' },
    { key:'chat', label:'AI Agent', icon:'sparkles', badge:'NEW' },
    { key:'pipeline', label:'My Offers', icon:'users' },
    { key:'calendar', label:'Viewings', icon:'cal' },
    { key:'documents', label:'My Documents', icon:'file' },
    { key:'automations', label:'Smart Alerts', icon:'play' },
    { key:'dashboard', label:'My Activity', icon:'chart' },
  ];

  return (
    <>
      {tweaks.showOrbs && <div className="app-bg"/>}
      {!tweaks.showOrbs && <div style={{position:'fixed',inset:0,background:'#080a10',zIndex:0}}/>}

      <div className="app-shell">
        {/* Titlebar */}
        <div className="titlebar">
          <div className="brand">
            <div className="brand-mark">S</div>
            <span>Sceptre <span style={{color:'#94a3b8',fontWeight:500}}>· Estate</span></span>
          </div>
          <div style={{flex:1}}/>
          <div style={{display:'flex',gap:8,alignItems:'center'}}>
            <span className="chip chip-sm" style={{display:'flex',alignItems:'center',gap:6}}>
              <span className="status-dot pulse"/> Live · UAE
            </span>
            <span className="chip chip-sm chip-mono">v0.4.2</span>
            <div className="avatar" style={{width:28,height:28,fontSize:11,marginLeft:6}}>LR</div>
          </div>
        </div>

        {/* Body */}
        <div className="body-region" data-screen-label="Sceptre Estate App">
          {/* Sidebar */}
          <div className="sidebar">
            <div className="sidebar-section">Workspace</div>
            {navItems.map(item => (
              <div key={item.key}
                data-screen-label={item.label}
                className={`nav-item ${route.name===item.key ? 'active' : ''}`}
                onClick={()=>goto(item.key)}>
                <Icon name={item.icon} size={17}/>
                <span style={{flex:1}}>{item.label}</span>
                {item.badge && <span className="badge">{item.badge}</span>}
              </div>
            ))}

            <div className="sidebar-section" style={{marginTop:'auto'}}>Saved</div>
            <div className="nav-item" style={{fontSize:12}}>
              <Icon name="heart" size={15}/>
              <span style={{flex:1}}>Wishlist</span>
              <span style={{fontSize:10,color:'#94a3b8',fontFamily:'var(--scp-font-mono)'}}>4</span>
            </div>
            <div className="nav-item" style={{fontSize:12}}>
              <Icon name="search" size={15}/>
              <span style={{flex:1}}>Saved searches</span>
              <span style={{fontSize:10,color:'#94a3b8',fontFamily:'var(--scp-font-mono)'}}>3</span>
            </div>

            {/* Settings */}
            <div style={{paddingTop:14,marginTop:14,borderTop:'1px solid rgba(255,255,255,0.06)'}}>
              <div className="nav-item" style={{fontSize:12}}>
                <Icon name="cog" size={15}/>
                <span>Settings</span>
              </div>
            </div>
          </div>

          {/* Main */}
          <div className="main">
            <div className="main-scroll" style={{
              padding: tweaks.density==='compact' ? '20px 24px' : '28px 32px',
            }}>
              {route.name==='browse' && <window.BrowseScreen
                onOpenProperty={openProperty}
                onOpenChat={()=>openChat()}
                view={browseView}
                setView={(v)=>{setBrowseView(v);setTweak({browseView:v});}}/>}
              {route.name==='detail' && <window.PropertyDetailScreen
                prop={route.prop} onBack={()=>goto('browse')}
                onOpenChat={()=>openChat(route.prop)}/>}
              {route.name==='chat' && <window.ChatScreen
                contextProp={route.contextProp}
                onOpenProperty={openProperty}/>}
              {route.name==='pipeline' && <window.PipelineScreen/>}
              {route.name==='dashboard' && <window.DashboardScreen/>}
              {route.name==='automations' && <window.AutomationsScreen/>}
              {route.name==='documents' && <window.DocumentsScreen/>}
              {route.name==='calendar' && <window.CalendarScreen/>}
            </div>
          </div>
        </div>
      </div>

      {/* Tweaks panel */}
      <window.TweaksPanel title="Tweaks">
        <window.TweakSection title="Accent">
          <window.TweakRadio label="Accent hue"
            value={tweaks.accentHue}
            onChange={v=>setTweak({accentHue:v})}
            options={[
              {value:'cyan',label:'Cyan'},
              {value:'violet',label:'Violet'},
              {value:'emerald',label:'Emerald'},
              {value:'amber',label:'Amber'},
            ]}/>
        </window.TweakSection>
        <window.TweakSection title="Layout">
          <window.TweakRadio label="Browse view"
            value={tweaks.browseView}
            onChange={v=>setTweak({browseView:v})}
            options={[
              {value:'grid',label:'Grid'},
              {value:'split',label:'Map + list'},
            ]}/>
          <window.TweakRadio label="Density"
            value={tweaks.density}
            onChange={v=>setTweak({density:v})}
            options={[
              {value:'comfortable',label:'Comfortable'},
              {value:'compact',label:'Compact'},
            ]}/>
        </window.TweakSection>
        <window.TweakSection title="Atmosphere">
          <window.TweakToggle label="Background light orbs"
            value={tweaks.showOrbs}
            onChange={v=>setTweak({showOrbs:v})}/>
        </window.TweakSection>
      </window.TweaksPanel>
    </>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(<App/>);
