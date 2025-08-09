"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["2669"],{13539:function(e,t,r){r.a(e,(async function(e,a){try{r.d(t,{Bt:function(){return l}});r(39710);var o=r(57900),n=r(3574),i=r(43956),s=e([o]);o=(s.then?(await s)():s)[0];const d=["sunday","monday","tuesday","wednesday","thursday","friday","saturday"],l=e=>e.first_weekday===i.FS.language?"weekInfo"in Intl.Locale.prototype?new Intl.Locale(e.language).weekInfo.firstDay%7:(0,n.L)(e.language)%7:d.includes(e.first_weekday)?d.indexOf(e.first_weekday):1;a()}catch(d){a(d)}}))},60495:function(e,t,r){r.a(e,(async function(e,a){try{r.d(t,{G:function(){return l}});var o=r(57900),n=r(28105),i=r(58713),s=e([o,i]);[o,i]=s.then?(await s)():s;const d=(0,n.Z)((e=>new Intl.RelativeTimeFormat(e.language,{numeric:"auto"}))),l=(e,t,r,a=!0)=>{const o=(0,i.W)(e,r,t);return a?d(t).format(o.value,o.unit):Intl.NumberFormat(t.language,{style:"unit",unit:o.unit,unitDisplay:"long"}).format(Math.abs(o.value))};a()}catch(d){a(d)}}))},58713:function(e,t,r){r.a(e,(async function(e,a){try{r.d(t,{W:function(){return h}});r(87799);var o=r(7722),n=r(66233),i=r(41238),s=r(13539),d=e([s]);s=(d.then?(await d)():d)[0];const c=1e3,u=60,p=60*u;function h(e,t=Date.now(),r,a={}){const d=Object.assign(Object.assign({},g),a||{}),l=(+e-+t)/c;if(Math.abs(l)<d.second)return{value:Math.round(l),unit:"second"};const h=l/u;if(Math.abs(h)<d.minute)return{value:Math.round(h),unit:"minute"};const b=l/p;if(Math.abs(b)<d.hour)return{value:Math.round(b),unit:"hour"};const v=new Date(e),f=new Date(t);v.setHours(0,0,0,0),f.setHours(0,0,0,0);const m=(0,o.j)(v,f);if(0===m)return{value:Math.round(b),unit:"hour"};if(Math.abs(m)<d.day)return{value:m,unit:"day"};const _=(0,s.Bt)(r),y=(0,n.z)(v,{weekStartsOn:_}),x=(0,n.z)(f,{weekStartsOn:_}),w=(0,i.p)(y,x);if(0===w)return{value:m,unit:"day"};if(Math.abs(w)<d.week)return{value:w,unit:"week"};const k=v.getFullYear()-f.getFullYear(),$=12*k+v.getMonth()-f.getMonth();return 0===$?{value:w,unit:"week"}:Math.abs($)<d.month||0===k?{value:$,unit:"month"}:{value:Math.round(k),unit:"year"}}const g={second:45,minute:45,hour:22,day:5,week:4,month:11};a()}catch(l){a(l)}}))},13965:function(e,t,r){r(26847),r(27530);var a=r(73742),o=r(59048),n=r(7616);let i,s,d,l=e=>e;class c extends o.oi{render(){return(0,o.dy)(i||(i=l`
      ${0}
      <slot></slot>
    `),this.header?(0,o.dy)(s||(s=l`<h1 class="card-header">${0}</h1>`),this.header):o.Ld)}constructor(...e){super(...e),this.raised=!1}}c.styles=(0,o.iv)(d||(d=l`
    :host {
      background: var(
        --ha-card-background,
        var(--card-background-color, white)
      );
      -webkit-backdrop-filter: var(--ha-card-backdrop-filter, none);
      backdrop-filter: var(--ha-card-backdrop-filter, none);
      box-shadow: var(--ha-card-box-shadow, none);
      box-sizing: border-box;
      border-radius: var(--ha-card-border-radius, 12px);
      border-width: var(--ha-card-border-width, 1px);
      border-style: solid;
      border-color: var(--ha-card-border-color, var(--divider-color, #e0e0e0));
      color: var(--primary-text-color);
      display: block;
      transition: all 0.3s ease-out;
      position: relative;
    }

    :host([raised]) {
      border: none;
      box-shadow: var(
        --ha-card-box-shadow,
        0px 2px 1px -1px rgba(0, 0, 0, 0.2),
        0px 1px 1px 0px rgba(0, 0, 0, 0.14),
        0px 1px 3px 0px rgba(0, 0, 0, 0.12)
      );
    }

    .card-header,
    :host ::slotted(.card-header) {
      color: var(--ha-card-header-color, var(--primary-text-color));
      font-family: var(--ha-card-header-font-family, inherit);
      font-size: var(--ha-card-header-font-size, var(--ha-font-size-2xl));
      letter-spacing: -0.012em;
      line-height: var(--ha-line-height-expanded);
      padding: 12px 16px 16px;
      display: block;
      margin-block-start: 0px;
      margin-block-end: 0px;
      font-weight: var(--ha-font-weight-normal);
    }

    :host ::slotted(.card-content:not(:first-child)),
    slot:not(:first-child)::slotted(.card-content) {
      padding-top: 0px;
      margin-top: -8px;
    }

    :host ::slotted(.card-content) {
      padding: 16px;
    }

    :host ::slotted(.card-actions) {
      border-top: 1px solid var(--divider-color, #e8e8e8);
      padding: 8px;
    }
  `)),(0,a.__decorate)([(0,n.Cb)()],c.prototype,"header",void 0),(0,a.__decorate)([(0,n.Cb)({type:Boolean,reflect:!0})],c.prototype,"raised",void 0),c=(0,a.__decorate)([(0,n.Mo)("ha-card")],c)},83379:function(e,t,r){r.a(e,(async function(e,a){try{r.r(t),r.d(t,{HaIconOverflowMenu:function(){return x}});r(26847),r(81738),r(6989),r(27530);var o=r(73742),n=r(59048),i=r(7616),s=r(31733),d=r(77204),l=(r(51431),r(78645),r(40830),r(27341)),c=(r(72633),r(1963),e([l]));l=(c.then?(await c)():c)[0];let u,p,h,g,b,v,f,m,_=e=>e;const y="M12,16A2,2 0 0,1 14,18A2,2 0 0,1 12,20A2,2 0 0,1 10,18A2,2 0 0,1 12,16M12,10A2,2 0 0,1 14,12A2,2 0 0,1 12,14A2,2 0 0,1 10,12A2,2 0 0,1 12,10M12,4A2,2 0 0,1 14,6A2,2 0 0,1 12,8A2,2 0 0,1 10,6A2,2 0 0,1 12,4Z";class x extends n.oi{render(){return(0,n.dy)(u||(u=_`
      ${0}
    `),this.narrow?(0,n.dy)(p||(p=_` <!-- Collapsed representation for small screens -->
            <ha-md-button-menu
              @click=${0}
              positioning="popover"
            >
              <ha-icon-button
                .label=${0}
                .path=${0}
                slot="trigger"
              ></ha-icon-button>

              ${0}
            </ha-md-button-menu>`),this._handleIconOverflowMenuOpened,this.hass.localize("ui.common.overflow_menu"),y,this.items.map((e=>e.divider?(0,n.dy)(h||(h=_`<ha-md-divider
                      role="separator"
                      tabindex="-1"
                    ></ha-md-divider>`)):(0,n.dy)(g||(g=_`<ha-md-menu-item
                      ?disabled=${0}
                      .clickAction=${0}
                      class=${0}
                    >
                      <ha-svg-icon
                        slot="start"
                        class=${0}
                        .path=${0}
                      ></ha-svg-icon>
                      ${0}
                    </ha-md-menu-item> `),e.disabled,e.action,(0,s.$)({warning:Boolean(e.warning)}),(0,s.$)({warning:Boolean(e.warning)}),e.path,e.label)))):(0,n.dy)(b||(b=_`
            <!-- Icon representation for big screens -->
            ${0}
          `),this.items.map((e=>{var t;return e.narrowOnly?n.Ld:e.divider?(0,n.dy)(v||(v=_`<div role="separator"></div>`)):(0,n.dy)(f||(f=_`<ha-tooltip
                      .disabled=${0}
                      .content=${0}
                    >
                      <ha-icon-button
                        @click=${0}
                        .label=${0}
                        .path=${0}
                        ?disabled=${0}
                      ></ha-icon-button>
                    </ha-tooltip>`),!e.tooltip,null!==(t=e.tooltip)&&void 0!==t?t:"",e.action,e.label,e.path,e.disabled)}))))}_handleIconOverflowMenuOpened(e){e.stopPropagation()}static get styles(){return[d.Qx,(0,n.iv)(m||(m=_`
        :host {
          display: flex;
          justify-content: flex-end;
        }
        div[role="separator"] {
          border-right: 1px solid var(--divider-color);
          width: 1px;
        }
      `))]}constructor(...e){super(...e),this.items=[],this.narrow=!1}}(0,o.__decorate)([(0,i.Cb)({attribute:!1})],x.prototype,"hass",void 0),(0,o.__decorate)([(0,i.Cb)({type:Array})],x.prototype,"items",void 0),(0,o.__decorate)([(0,i.Cb)({type:Boolean})],x.prototype,"narrow",void 0),x=(0,o.__decorate)([(0,i.Mo)("ha-icon-overflow-menu")],x),a()}catch(u){a(u)}}))},27341:function(e,t,r){r.a(e,(async function(e,t){try{var a=r(73742),o=r(52634),n=r(62685),i=r(59048),s=r(7616),d=r(75535),l=e([o]);o=(l.then?(await l)():l)[0];let c,u=e=>e;(0,d.jx)("tooltip.show",{keyframes:[{opacity:0},{opacity:1}],options:{duration:150,easing:"ease"}}),(0,d.jx)("tooltip.hide",{keyframes:[{opacity:1},{opacity:0}],options:{duration:400,easing:"ease"}});class p extends o.Z{}p.styles=[n.Z,(0,i.iv)(c||(c=u`
      :host {
        --sl-tooltip-background-color: var(--secondary-background-color);
        --sl-tooltip-color: var(--primary-text-color);
        --sl-tooltip-font-family: var(
          --ha-tooltip-font-family,
          var(--ha-font-family-body)
        );
        --sl-tooltip-font-size: var(
          --ha-tooltip-font-size,
          var(--ha-font-size-s)
        );
        --sl-tooltip-font-weight: var(
          --ha-tooltip-font-weight,
          var(--ha-font-weight-normal)
        );
        --sl-tooltip-line-height: var(
          --ha-tooltip-line-height,
          var(--ha-line-height-condensed)
        );
        --sl-tooltip-padding: 8px;
        --sl-tooltip-border-radius: var(--ha-tooltip-border-radius, 4px);
        --sl-tooltip-arrow-size: var(--ha-tooltip-arrow-size, 8px);
        --sl-z-index-tooltip: var(--ha-tooltip-z-index, 1000);
      }
    `))],p=(0,a.__decorate)([(0,s.Mo)("ha-tooltip")],p),t()}catch(c){t(c)}}))},15724:function(e,t,r){r.d(t,{q:function(){return l}});r(40777),r(39710),r(56389),r(26847),r(70820),r(64455),r(40005),r(27530);const a=/^[v^~<>=]*?(\d+)(?:\.([x*]|\d+)(?:\.([x*]|\d+)(?:\.([x*]|\d+))?(?:-([\da-z\-]+(?:\.[\da-z\-]+)*))?(?:\+[\da-z\-]+(?:\.[\da-z\-]+)*)?)?)?$/i,o=e=>{if("string"!=typeof e)throw new TypeError("Invalid argument expected string");const t=e.match(a);if(!t)throw new Error(`Invalid argument not valid semver ('${e}' received)`);return t.shift(),t},n=e=>"*"===e||"x"===e||"X"===e,i=e=>{const t=parseInt(e,10);return isNaN(t)?e:t},s=(e,t)=>{if(n(e)||n(t))return 0;const[r,a]=((e,t)=>typeof e!=typeof t?[String(e),String(t)]:[e,t])(i(e),i(t));return r>a?1:r<a?-1:0},d=(e,t)=>{for(let r=0;r<Math.max(e.length,t.length);r++){const a=s(e[r]||"0",t[r]||"0");if(0!==a)return a}return 0},l=(e,t,r)=>{p(r);const a=((e,t)=>{const r=o(e),a=o(t),n=r.pop(),i=a.pop(),s=d(r,a);return 0!==s?s:n&&i?d(n.split("."),i.split(".")):n||i?n?-1:1:0})(e,t);return c[r].includes(a)},c={">":[1],">=":[0,1],"=":[0],"<=":[-1,0],"<":[-1],"!=":[-1,1]},u=Object.keys(c),p=e=>{if("string"!=typeof e)throw new TypeError("Invalid operator type, expected string but got "+typeof e);if(-1===u.indexOf(e))throw new Error(`Invalid operator, expected one of ${u.join("|")}`)}},92799:function(e,t,r){r(26847),r(44438),r(81738),r(22960),r(6989),r(93190),r(27530);var a=r(73742),o=r(59048),n=r(7616),i=r(31733),s=r(29740),d=r(38059);let l,c,u,p,h,g,b=e=>e;const v=new d.r("knx-project-tree-view");class f extends o.oi{connectedCallback(){super.connectedCallback();const e=t=>{Object.entries(t).forEach((([t,r])=>{r.group_addresses.length>0&&(this._selectableRanges[t]={selected:!1,groupAddresses:r.group_addresses}),e(r.group_ranges)}))};e(this.data.group_ranges),v.debug("ranges",this._selectableRanges)}render(){return(0,o.dy)(l||(l=b`<div class="ha-tree-view">${0}</div>`),this._recurseData(this.data.group_ranges))}_recurseData(e,t=0){const r=Object.entries(e).map((([e,r])=>{const a=Object.keys(r.group_ranges).length>0;if(!(a||r.group_addresses.length>0))return o.Ld;const n=e in this._selectableRanges,s=!!n&&this._selectableRanges[e].selected,d={"range-item":!0,"root-range":0===t,"sub-range":t>0,selectable:n,"selected-range":s,"non-selected-range":n&&!s},l=(0,o.dy)(c||(c=b`<div
        class=${0}
        toggle-range=${0}
        @click=${0}
      >
        <span class="range-key">${0}</span>
        <span class="range-text">${0}</span>
      </div>`),(0,i.$)(d),n?e:o.Ld,n?this.multiselect?this._selectionChangedMulti:this._selectionChangedSingle:o.Ld,e,r.name);if(a){const e={"root-group":0===t,"sub-group":0!==t};return(0,o.dy)(u||(u=b`<div class=${0}>
          ${0} ${0}
        </div>`),(0,i.$)(e),l,this._recurseData(r.group_ranges,t+1))}return(0,o.dy)(p||(p=b`${0}`),l)}));return(0,o.dy)(h||(h=b`${0}`),r)}_selectionChangedMulti(e){const t=e.target.getAttribute("toggle-range");this._selectableRanges[t].selected=!this._selectableRanges[t].selected,this._selectionUpdate(),this.requestUpdate()}_selectionChangedSingle(e){const t=e.target.getAttribute("toggle-range"),r=this._selectableRanges[t].selected;Object.values(this._selectableRanges).forEach((e=>{e.selected=!1})),this._selectableRanges[t].selected=!r,this._selectionUpdate(),this.requestUpdate()}_selectionUpdate(){const e=Object.values(this._selectableRanges).reduce(((e,t)=>t.selected?e.concat(t.groupAddresses):e),[]);v.debug("selection changed",e),(0,s.B)(this,"knx-group-range-selection-changed",{groupAddresses:e})}constructor(...e){super(...e),this.multiselect=!1,this._selectableRanges={}}}f.styles=(0,o.iv)(g||(g=b`
    :host {
      margin: 0;
      height: 100%;
      overflow-y: scroll;
      overflow-x: hidden;
      background-color: var(--card-background-color);
    }

    .ha-tree-view {
      cursor: default;
    }

    .root-group {
      margin-bottom: 8px;
    }

    .root-group > * {
      padding-top: 5px;
      padding-bottom: 5px;
    }

    .range-item {
      display: block;
      overflow: hidden;
      white-space: nowrap;
      text-overflow: ellipsis;
      font-size: 0.875rem;
    }

    .range-item > * {
      vertical-align: middle;
      pointer-events: none;
    }

    .range-key {
      color: var(--text-primary-color);
      font-size: 0.75rem;
      font-weight: 700;
      background-color: var(--label-badge-grey);
      border-radius: 4px;
      padding: 1px 4px;
      margin-right: 2px;
    }

    .root-range {
      padding-left: 8px;
      font-weight: 500;
      background-color: var(--secondary-background-color);

      & .range-key {
        color: var(--primary-text-color);
        background-color: var(--card-background-color);
      }
    }

    .sub-range {
      padding-left: 13px;
    }

    .selectable {
      cursor: pointer;
    }

    .selectable:hover {
      background-color: rgba(var(--rgb-primary-text-color), 0.04);
    }

    .selected-range {
      background-color: rgba(var(--rgb-primary-color), 0.12);

      & .range-key {
        background-color: var(--primary-color);
      }
    }

    .selected-range:hover {
      background-color: rgba(var(--rgb-primary-color), 0.07);
    }

    .non-selected-range {
      background-color: var(--card-background-color);
    }
  `)),(0,a.__decorate)([(0,n.Cb)({attribute:!1})],f.prototype,"data",void 0),(0,a.__decorate)([(0,n.Cb)({attribute:!1})],f.prototype,"multiselect",void 0),(0,a.__decorate)([(0,n.SB)()],f.prototype,"_selectableRanges",void 0),f=(0,a.__decorate)([(0,n.Mo)("knx-project-tree-view")],f)},65793:function(e,t,r){r.d(t,{Am:function(){return d},Wl:function(){return n},Yh:function(){return i},f3:function(){return o},jQ:function(){return v},q$:function(){return s},tu:function(){return b}});r(44438),r(81738),r(93190),r(64455),r(56303),r(40005);var a=r(24110);const o={payload:e=>null==e.payload?"":Array.isArray(e.payload)?e.payload.reduce(((e,t)=>e+t.toString(16).padStart(2,"0")),"0x"):e.payload.toString(),valueWithUnit:e=>null==e.value?"":"number"==typeof e.value||"boolean"==typeof e.value||"string"==typeof e.value?e.value.toString()+(e.unit?" "+e.unit:""):(0,a.$w)(e.value),timeWithMilliseconds:e=>new Date(e.timestamp).toLocaleTimeString(["en-US"],{hour12:!1,hour:"2-digit",minute:"2-digit",second:"2-digit",fractionalSecondDigits:3}),dateWithMilliseconds:e=>new Date(e.timestamp).toLocaleTimeString([],{year:"numeric",month:"2-digit",day:"2-digit",hour:"2-digit",minute:"2-digit",second:"2-digit",fractionalSecondDigits:3}),dptNumber:e=>null==e.dpt_main?"":null==e.dpt_sub?e.dpt_main.toString():e.dpt_main.toString()+"."+e.dpt_sub.toString().padStart(3,"0"),dptNameNumber:e=>{const t=o.dptNumber(e);return null==e.dpt_name?`DPT ${t}`:t?`DPT ${t} ${e.dpt_name}`:e.dpt_name}},n=e=>null==e?"":e.main+(e.sub?"."+e.sub.toString().padStart(3,"0"):""),i=e=>e.toLocaleTimeString(void 0,{hour12:!1,hour:"2-digit",minute:"2-digit",second:"2-digit",fractionalSecondDigits:3}),s=e=>e.toLocaleDateString(void 0,{year:"numeric",month:"2-digit",day:"2-digit"})+", "+e.toLocaleTimeString(void 0,{hour12:!1,hour:"2-digit",minute:"2-digit",second:"2-digit",fractionalSecondDigits:3}),d=e=>{const t=new Date(e),r=e.match(/\.(\d{6})/),a=r?r[1]:"000000";return t.toLocaleDateString(void 0,{year:"numeric",month:"2-digit",day:"2-digit"})+", "+t.toLocaleTimeString(void 0,{hour12:!1,hour:"2-digit",minute:"2-digit",second:"2-digit"})+"."+a},l=1e3,c=1e3,u=60*c,p=60*u,h=2,g=3;function b(e){const t=e.indexOf(".");if(-1===t)return 1e3*Date.parse(e);let r=e.indexOf("Z",t);-1===r&&(r=e.indexOf("+",t),-1===r&&(r=e.indexOf("-",t))),-1===r&&(r=e.length);const a=e.slice(0,t)+e.slice(r),o=Date.parse(a);let n=e.slice(t+1,r);return n.length<6?n=n.padEnd(6,"0"):n.length>6&&(n=n.slice(0,6)),1e3*o+Number(n)}function v(e,t="milliseconds"){if(null==e)return"—";const r=e<0?"-":"",a=Math.abs(e),o="milliseconds"===t?Math.round(a/l):Math.floor(a/l),n="microseconds"===t?a%l:0,i=Math.floor(o/p),s=Math.floor(o%p/u),d=Math.floor(o%u/c),b=o%c,v=e=>e.toString().padStart(h,"0"),f=e=>e.toString().padStart(g,"0"),m="microseconds"===t?`.${f(b)}${f(n)}`:`.${f(b)}`,_=`${v(s)}:${v(d)}`;return`${r}${i>0?`${v(i)}:${_}`:_}${m}`}},18988:function(e,t,r){r.a(e,(async function(e,a){try{r.r(t),r.d(t,{KNXProjectView:function(){return D}});r(39710),r(26847),r(2394),r(44438),r(81738),r(93190),r(87799),r(1455),r(56303),r(56389),r(27530);var o=r(73742),n=r(59048),i=r(7616),s=r(28105),d=r(29173),l=r(86829),c=(r(62790),r(13965),r(78645),r(83379)),u=(r(32780),r(60495)),p=(r(92799),r(15724)),h=r(63279),g=r(38059),b=r(65793),v=e([l,c,u]);[l,c,u]=v.then?(await v)():v;let f,m,_,y,x,w,k,$,j,M,S,A,z=e=>e;const C="M6,13H18V11H6M3,6V8H21V6M10,18H14V16H10V18Z",H="M19,13H13V19H11V13H5V11H11V5H13V11H19V13Z",O="M18 7C16.9 7 16 7.9 16 9V15C16 16.1 16.9 17 18 17H20C21.1 17 22 16.1 22 15V11H20V15H18V9H22V7H18M2 7V17H8V15H4V7H2M11 7C9.9 7 9 7.9 9 9V15C9 16.1 9.9 17 11 17H13C14.1 17 15 16.1 15 15V9C15 7.9 14.1 7 13 7H11M11 9H13V15H11V9Z",R=new g.r("knx-project-view"),V="3.3.0";class D extends n.oi{disconnectedCallback(){super.disconnectedCallback(),this._subscribed&&(this._subscribed(),this._subscribed=void 0)}async firstUpdated(){this.knx.project?this._isGroupRangeAvailable():this.knx.loadProject().then((()=>{this._isGroupRangeAvailable(),this.requestUpdate()})),(0,h.ze)(this.hass).then((e=>{this._lastTelegrams=e})).catch((e=>{R.error("getGroupTelegrams",e),(0,d.c)("/knx/error",{replace:!0,data:e})})),this._subscribed=await(0,h.IP)(this.hass,(e=>{this.telegram_callback(e)}))}_isGroupRangeAvailable(){var e,t;const r=null!==(e=null===(t=this.knx.project)||void 0===t?void 0:t.knxproject.info.xknxproject_version)&&void 0!==e?e:"0.0.0";R.debug("project version: "+r),this._groupRangeAvailable=(0,p.q)(r,V,">=")}telegram_callback(e){this._lastTelegrams=Object.assign(Object.assign({},this._lastTelegrams),{},{[e.destination]:e})}_groupAddressMenu(e){var t;const r=[];return r.push({path:O,label:this.knx.localize("project_view_menu_view_telegrams"),action:()=>{(0,d.c)(`/knx/group_monitor?destination=${e.address}`)}}),1===(null===(t=e.dpt)||void 0===t?void 0:t.main)&&r.push({path:H,label:this.knx.localize("project_view_menu_create_binary_sensor"),action:()=>{(0,d.c)("/knx/entities/create/binary_sensor?knx.ga_sensor.state="+e.address)}}),(0,n.dy)(f||(f=z`
      <ha-icon-overflow-menu .hass=${0} narrow .items=${0}> </ha-icon-overflow-menu>
    `),this.hass,r)}_getRows(e){return e.length?Object.entries(this.knx.project.knxproject.group_addresses).reduce(((t,[r,a])=>(e.includes(r)&&t.push(a),t)),[]):Object.values(this.knx.project.knxproject.group_addresses)}_visibleAddressesChanged(e){this._visibleGroupAddresses=e.detail.groupAddresses}render(){if(!this.hass||!this.knx.project)return(0,n.dy)(m||(m=z` <hass-loading-screen></hass-loading-screen> `));const e=this._getRows(this._visibleGroupAddresses);return(0,n.dy)(_||(_=z`
      <hass-tabs-subpage
        .hass=${0}
        .narrow=${0}
        .route=${0}
        .tabs=${0}
        .localizeFunc=${0}
      >
        ${0}
      </hass-tabs-subpage>
    `),this.hass,this.narrow,this.route,this.tabs,this.knx.localize,this.knx.project.project_loaded?(0,n.dy)(y||(y=z`${0}
              <div class="sections">
                ${0}
                <ha-data-table
                  class="ga-table"
                  .hass=${0}
                  .columns=${0}
                  .data=${0}
                  .hasFab=${0}
                  .searchLabel=${0}
                  .clickable=${0}
                ></ha-data-table>
              </div>`),this.narrow&&this._groupRangeAvailable?(0,n.dy)(x||(x=z`<ha-icon-button
                    slot="toolbar-icon"
                    .label=${0}
                    .path=${0}
                    @click=${0}
                  ></ha-icon-button>`),this.hass.localize("ui.components.related-filter-menu.filter"),C,this._toggleRangeSelector):n.Ld,this._groupRangeAvailable?(0,n.dy)(w||(w=z`
                      <knx-project-tree-view
                        .data=${0}
                        @knx-group-range-selection-changed=${0}
                      ></knx-project-tree-view>
                    `),this.knx.project.knxproject,this._visibleAddressesChanged):n.Ld,this.hass,this._columns(this.narrow,this.hass.language),e,!1,this.hass.localize("ui.components.data-table.search"),!1):(0,n.dy)(k||(k=z` <ha-card .header=${0}>
              <div class="card-content">
                <p>${0}</p>
              </div>
            </ha-card>`),this.knx.localize("attention"),this.knx.localize("project_view_upload")))}_toggleRangeSelector(){this.rangeSelectorHidden=!this.rangeSelectorHidden}constructor(...e){super(...e),this.rangeSelectorHidden=!0,this._visibleGroupAddresses=[],this._groupRangeAvailable=!1,this._lastTelegrams={},this._columns=(0,s.Z)(((e,t)=>({address:{filterable:!0,sortable:!0,title:this.knx.localize("project_view_table_address"),flex:1,minWidth:"100px"},name:{filterable:!0,sortable:!0,title:this.knx.localize("project_view_table_name"),flex:3},dpt:{sortable:!0,filterable:!0,title:this.knx.localize("project_view_table_dpt"),flex:1,minWidth:"82px",template:e=>e.dpt?(0,n.dy)($||($=z`<span style="display:inline-block;width:24px;text-align:right;"
                  >${0}</span
                >${0} `),e.dpt.main,e.dpt.sub?"."+e.dpt.sub.toString().padStart(3,"0"):""):""},lastValue:{filterable:!0,title:this.knx.localize("project_view_table_last_value"),flex:2,template:e=>{const t=this._lastTelegrams[e.address];if(!t)return"";const r=b.f3.payload(t);return null==t.value?(0,n.dy)(j||(j=z`<code>${0}</code>`),r):(0,n.dy)(M||(M=z`<div title=${0}>
            ${0}
          </div>`),r,b.f3.valueWithUnit(this._lastTelegrams[e.address]))}},updated:{title:this.knx.localize("project_view_table_updated"),flex:1,showNarrow:!1,template:e=>{const t=this._lastTelegrams[e.address];if(!t)return"";const r=`${b.f3.dateWithMilliseconds(t)}\n\n${t.source} ${t.source_name}`;return(0,n.dy)(S||(S=z`<div title=${0}>
            ${0}
          </div>`),r,(0,u.G)(new Date(t.timestamp),this.hass.locale))}},actions:{title:"",minWidth:"72px",type:"overflow-menu",template:e=>this._groupAddressMenu(e)}})))}}D.styles=(0,n.iv)(A||(A=z`
    hass-loading-screen {
      --app-header-background-color: var(--sidebar-background-color);
      --app-header-text-color: var(--sidebar-text-color);
    }
    .sections {
      display: flex;
      flex-direction: row;
      height: 100%;
    }

    :host([narrow]) knx-project-tree-view {
      position: absolute;
      max-width: calc(100% - 60px); /* 100% -> max 871px before not narrow */
      z-index: 1;
      right: 0;
      transition: 0.5s;
      border-left: 1px solid var(--divider-color);
    }

    :host([narrow][range-selector-hidden]) knx-project-tree-view {
      width: 0;
    }

    :host(:not([narrow])) knx-project-tree-view {
      max-width: 255px; /* min 616px - 816px for tree-view + ga-table (depending on side menu) */
    }

    .ga-table {
      flex: 1;
    }
  `)),(0,o.__decorate)([(0,i.Cb)({type:Object})],D.prototype,"hass",void 0),(0,o.__decorate)([(0,i.Cb)({attribute:!1})],D.prototype,"knx",void 0),(0,o.__decorate)([(0,i.Cb)({type:Boolean,reflect:!0})],D.prototype,"narrow",void 0),(0,o.__decorate)([(0,i.Cb)({type:Object})],D.prototype,"route",void 0),(0,o.__decorate)([(0,i.Cb)({type:Array,reflect:!1})],D.prototype,"tabs",void 0),(0,o.__decorate)([(0,i.Cb)({type:Boolean,reflect:!0,attribute:"range-selector-hidden"})],D.prototype,"rangeSelectorHidden",void 0),(0,o.__decorate)([(0,i.SB)()],D.prototype,"_visibleGroupAddresses",void 0),(0,o.__decorate)([(0,i.SB)()],D.prototype,"_groupRangeAvailable",void 0),(0,o.__decorate)([(0,i.SB)()],D.prototype,"_subscribed",void 0),(0,o.__decorate)([(0,i.SB)()],D.prototype,"_lastTelegrams",void 0),D=(0,o.__decorate)([(0,i.Mo)("knx-project-view")],D),a()}catch(f){a(f)}}))}}]);
//# sourceMappingURL=2669.6cd9a30040ddf394.js.map