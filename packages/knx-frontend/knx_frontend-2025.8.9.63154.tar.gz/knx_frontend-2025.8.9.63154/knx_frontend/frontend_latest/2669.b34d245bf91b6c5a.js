export const __webpack_ids__=["2669"];export const __webpack_modules__={13539:function(e,t,a){a.d(t,{Bt:()=>n});var r=a(3574),o=a(1066);const i=["sunday","monday","tuesday","wednesday","thursday","friday","saturday"],n=e=>e.first_weekday===o.FS.language?"weekInfo"in Intl.Locale.prototype?new Intl.Locale(e.language).weekInfo.firstDay%7:(0,r.L)(e.language)%7:i.includes(e.first_weekday)?i.indexOf(e.first_weekday):1},60495:function(e,t,a){a.a(e,(async function(e,r){try{a.d(t,{G:()=>l});var o=a(57900),i=a(28105),n=a(58713),s=e([o,n]);[o,n]=s.then?(await s)():s;const d=(0,i.Z)((e=>new Intl.RelativeTimeFormat(e.language,{numeric:"auto"}))),l=(e,t,a,r=!0)=>{const o=(0,n.W)(e,a,t);return r?d(t).format(o.value,o.unit):Intl.NumberFormat(t.language,{style:"unit",unit:o.unit,unitDisplay:"long"}).format(Math.abs(o.value))};r()}catch(d){r(d)}}))},58713:function(e,t,a){a.a(e,(async function(e,r){try{a.d(t,{W:()=>h});var o=a(7722),i=a(66233),n=a(41238),s=a(13539);const l=1e3,c=60,p=60*c;function h(e,t=Date.now(),a,r={}){const d={...u,...r||{}},h=(+e-+t)/l;if(Math.abs(h)<d.second)return{value:Math.round(h),unit:"second"};const g=h/c;if(Math.abs(g)<d.minute)return{value:Math.round(g),unit:"minute"};const b=h/p;if(Math.abs(b)<d.hour)return{value:Math.round(b),unit:"hour"};const v=new Date(e),_=new Date(t);v.setHours(0,0,0,0),_.setHours(0,0,0,0);const m=(0,o.j)(v,_);if(0===m)return{value:Math.round(b),unit:"hour"};if(Math.abs(m)<d.day)return{value:m,unit:"day"};const y=(0,s.Bt)(a),f=(0,i.z)(v,{weekStartsOn:y}),x=(0,i.z)(_,{weekStartsOn:y}),w=(0,n.p)(f,x);if(0===w)return{value:m,unit:"day"};if(Math.abs(w)<d.week)return{value:w,unit:"week"};const k=v.getFullYear()-_.getFullYear(),$=12*k+v.getMonth()-_.getMonth();return 0===$?{value:w,unit:"week"}:Math.abs($)<d.month||0===k?{value:$,unit:"month"}:{value:Math.round(k),unit:"year"}}const u={second:45,minute:45,hour:22,day:5,week:4,month:11};r()}catch(d){r(d)}}))},13965:function(e,t,a){var r=a(73742),o=a(59048),i=a(7616);class n extends o.oi{render(){return o.dy`
      ${this.header?o.dy`<h1 class="card-header">${this.header}</h1>`:o.Ld}
      <slot></slot>
    `}constructor(...e){super(...e),this.raised=!1}}n.styles=o.iv`
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
  `,(0,r.__decorate)([(0,i.Cb)()],n.prototype,"header",void 0),(0,r.__decorate)([(0,i.Cb)({type:Boolean,reflect:!0})],n.prototype,"raised",void 0),n=(0,r.__decorate)([(0,i.Mo)("ha-card")],n)},83379:function(e,t,a){a.a(e,(async function(e,r){try{a.r(t),a.d(t,{HaIconOverflowMenu:()=>h});var o=a(73742),i=a(59048),n=a(7616),s=a(31733),d=a(77204),l=(a(51431),a(78645),a(40830),a(27341)),c=(a(72633),a(1963),e([l]));l=(c.then?(await c)():c)[0];const p="M12,16A2,2 0 0,1 14,18A2,2 0 0,1 12,20A2,2 0 0,1 10,18A2,2 0 0,1 12,16M12,10A2,2 0 0,1 14,12A2,2 0 0,1 12,14A2,2 0 0,1 10,12A2,2 0 0,1 12,10M12,4A2,2 0 0,1 14,6A2,2 0 0,1 12,8A2,2 0 0,1 10,6A2,2 0 0,1 12,4Z";class h extends i.oi{render(){return i.dy`
      ${this.narrow?i.dy` <!-- Collapsed representation for small screens -->
            <ha-md-button-menu
              @click=${this._handleIconOverflowMenuOpened}
              positioning="popover"
            >
              <ha-icon-button
                .label=${this.hass.localize("ui.common.overflow_menu")}
                .path=${p}
                slot="trigger"
              ></ha-icon-button>

              ${this.items.map((e=>e.divider?i.dy`<ha-md-divider
                      role="separator"
                      tabindex="-1"
                    ></ha-md-divider>`:i.dy`<ha-md-menu-item
                      ?disabled=${e.disabled}
                      .clickAction=${e.action}
                      class=${(0,s.$)({warning:Boolean(e.warning)})}
                    >
                      <ha-svg-icon
                        slot="start"
                        class=${(0,s.$)({warning:Boolean(e.warning)})}
                        .path=${e.path}
                      ></ha-svg-icon>
                      ${e.label}
                    </ha-md-menu-item> `))}
            </ha-md-button-menu>`:i.dy`
            <!-- Icon representation for big screens -->
            ${this.items.map((e=>e.narrowOnly?i.Ld:e.divider?i.dy`<div role="separator"></div>`:i.dy`<ha-tooltip
                      .disabled=${!e.tooltip}
                      .content=${e.tooltip??""}
                    >
                      <ha-icon-button
                        @click=${e.action}
                        .label=${e.label}
                        .path=${e.path}
                        ?disabled=${e.disabled}
                      ></ha-icon-button>
                    </ha-tooltip>`))}
          `}
    `}_handleIconOverflowMenuOpened(e){e.stopPropagation()}static get styles(){return[d.Qx,i.iv`
        :host {
          display: flex;
          justify-content: flex-end;
        }
        div[role="separator"] {
          border-right: 1px solid var(--divider-color);
          width: 1px;
        }
      `]}constructor(...e){super(...e),this.items=[],this.narrow=!1}}(0,o.__decorate)([(0,n.Cb)({attribute:!1})],h.prototype,"hass",void 0),(0,o.__decorate)([(0,n.Cb)({type:Array})],h.prototype,"items",void 0),(0,o.__decorate)([(0,n.Cb)({type:Boolean})],h.prototype,"narrow",void 0),h=(0,o.__decorate)([(0,n.Mo)("ha-icon-overflow-menu")],h),r()}catch(p){r(p)}}))},27341:function(e,t,a){a.a(e,(async function(e,t){try{var r=a(73742),o=a(52634),i=a(62685),n=a(59048),s=a(7616),d=a(75535),l=e([o]);o=(l.then?(await l)():l)[0],(0,d.jx)("tooltip.show",{keyframes:[{opacity:0},{opacity:1}],options:{duration:150,easing:"ease"}}),(0,d.jx)("tooltip.hide",{keyframes:[{opacity:1},{opacity:0}],options:{duration:400,easing:"ease"}});class c extends o.Z{}c.styles=[i.Z,n.iv`
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
    `],c=(0,r.__decorate)([(0,s.Mo)("ha-tooltip")],c),t()}catch(c){t(c)}}))},15724:function(e,t,a){a.d(t,{q:()=>l});const r=/^[v^~<>=]*?(\d+)(?:\.([x*]|\d+)(?:\.([x*]|\d+)(?:\.([x*]|\d+))?(?:-([\da-z\-]+(?:\.[\da-z\-]+)*))?(?:\+[\da-z\-]+(?:\.[\da-z\-]+)*)?)?)?$/i,o=e=>{if("string"!=typeof e)throw new TypeError("Invalid argument expected string");const t=e.match(r);if(!t)throw new Error(`Invalid argument not valid semver ('${e}' received)`);return t.shift(),t},i=e=>"*"===e||"x"===e||"X"===e,n=e=>{const t=parseInt(e,10);return isNaN(t)?e:t},s=(e,t)=>{if(i(e)||i(t))return 0;const[a,r]=((e,t)=>typeof e!=typeof t?[String(e),String(t)]:[e,t])(n(e),n(t));return a>r?1:a<r?-1:0},d=(e,t)=>{for(let a=0;a<Math.max(e.length,t.length);a++){const r=s(e[a]||"0",t[a]||"0");if(0!==r)return r}return 0},l=(e,t,a)=>{h(a);const r=((e,t)=>{const a=o(e),r=o(t),i=a.pop(),n=r.pop(),s=d(a,r);return 0!==s?s:i&&n?d(i.split("."),n.split(".")):i||n?i?-1:1:0})(e,t);return c[a].includes(r)},c={">":[1],">=":[0,1],"=":[0],"<=":[-1,0],"<":[-1],"!=":[-1,1]},p=Object.keys(c),h=e=>{if("string"!=typeof e)throw new TypeError("Invalid operator type, expected string but got "+typeof e);if(-1===p.indexOf(e))throw new Error(`Invalid operator, expected one of ${p.join("|")}`)}},92799:function(e,t,a){var r=a(73742),o=a(59048),i=a(7616),n=a(31733),s=a(29740);const d=new(a(38059).r)("knx-project-tree-view");class l extends o.oi{connectedCallback(){super.connectedCallback();const e=t=>{Object.entries(t).forEach((([t,a])=>{a.group_addresses.length>0&&(this._selectableRanges[t]={selected:!1,groupAddresses:a.group_addresses}),e(a.group_ranges)}))};e(this.data.group_ranges),d.debug("ranges",this._selectableRanges)}render(){return o.dy`<div class="ha-tree-view">${this._recurseData(this.data.group_ranges)}</div>`}_recurseData(e,t=0){const a=Object.entries(e).map((([e,a])=>{const r=Object.keys(a.group_ranges).length>0;if(!(r||a.group_addresses.length>0))return o.Ld;const i=e in this._selectableRanges,s=!!i&&this._selectableRanges[e].selected,d={"range-item":!0,"root-range":0===t,"sub-range":t>0,selectable:i,"selected-range":s,"non-selected-range":i&&!s},l=o.dy`<div
        class=${(0,n.$)(d)}
        toggle-range=${i?e:o.Ld}
        @click=${i?this.multiselect?this._selectionChangedMulti:this._selectionChangedSingle:o.Ld}
      >
        <span class="range-key">${e}</span>
        <span class="range-text">${a.name}</span>
      </div>`;if(r){const e={"root-group":0===t,"sub-group":0!==t};return o.dy`<div class=${(0,n.$)(e)}>
          ${l} ${this._recurseData(a.group_ranges,t+1)}
        </div>`}return o.dy`${l}`}));return o.dy`${a}`}_selectionChangedMulti(e){const t=e.target.getAttribute("toggle-range");this._selectableRanges[t].selected=!this._selectableRanges[t].selected,this._selectionUpdate(),this.requestUpdate()}_selectionChangedSingle(e){const t=e.target.getAttribute("toggle-range"),a=this._selectableRanges[t].selected;Object.values(this._selectableRanges).forEach((e=>{e.selected=!1})),this._selectableRanges[t].selected=!a,this._selectionUpdate(),this.requestUpdate()}_selectionUpdate(){const e=Object.values(this._selectableRanges).reduce(((e,t)=>t.selected?e.concat(t.groupAddresses):e),[]);d.debug("selection changed",e),(0,s.B)(this,"knx-group-range-selection-changed",{groupAddresses:e})}constructor(...e){super(...e),this.multiselect=!1,this._selectableRanges={}}}l.styles=o.iv`
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
  `,(0,r.__decorate)([(0,i.Cb)({attribute:!1})],l.prototype,"data",void 0),(0,r.__decorate)([(0,i.Cb)({attribute:!1})],l.prototype,"multiselect",void 0),(0,r.__decorate)([(0,i.SB)()],l.prototype,"_selectableRanges",void 0),l=(0,r.__decorate)([(0,i.Mo)("knx-project-tree-view")],l)},65793:function(e,t,a){a.d(t,{Am:()=>d,Wl:()=>i,Yh:()=>n,f3:()=>o,jQ:()=>v,q$:()=>s,tu:()=>b});var r=a(24110);const o={payload:e=>null==e.payload?"":Array.isArray(e.payload)?e.payload.reduce(((e,t)=>e+t.toString(16).padStart(2,"0")),"0x"):e.payload.toString(),valueWithUnit:e=>null==e.value?"":"number"==typeof e.value||"boolean"==typeof e.value||"string"==typeof e.value?e.value.toString()+(e.unit?" "+e.unit:""):(0,r.$w)(e.value),timeWithMilliseconds:e=>new Date(e.timestamp).toLocaleTimeString(["en-US"],{hour12:!1,hour:"2-digit",minute:"2-digit",second:"2-digit",fractionalSecondDigits:3}),dateWithMilliseconds:e=>new Date(e.timestamp).toLocaleTimeString([],{year:"numeric",month:"2-digit",day:"2-digit",hour:"2-digit",minute:"2-digit",second:"2-digit",fractionalSecondDigits:3}),dptNumber:e=>null==e.dpt_main?"":null==e.dpt_sub?e.dpt_main.toString():e.dpt_main.toString()+"."+e.dpt_sub.toString().padStart(3,"0"),dptNameNumber:e=>{const t=o.dptNumber(e);return null==e.dpt_name?`DPT ${t}`:t?`DPT ${t} ${e.dpt_name}`:e.dpt_name}},i=e=>null==e?"":e.main+(e.sub?"."+e.sub.toString().padStart(3,"0"):""),n=e=>e.toLocaleTimeString(void 0,{hour12:!1,hour:"2-digit",minute:"2-digit",second:"2-digit",fractionalSecondDigits:3}),s=e=>e.toLocaleDateString(void 0,{year:"numeric",month:"2-digit",day:"2-digit"})+", "+e.toLocaleTimeString(void 0,{hour12:!1,hour:"2-digit",minute:"2-digit",second:"2-digit",fractionalSecondDigits:3}),d=e=>{const t=new Date(e),a=e.match(/\.(\d{6})/),r=a?a[1]:"000000";return t.toLocaleDateString(void 0,{year:"numeric",month:"2-digit",day:"2-digit"})+", "+t.toLocaleTimeString(void 0,{hour12:!1,hour:"2-digit",minute:"2-digit",second:"2-digit"})+"."+r},l=1e3,c=1e3,p=60*c,h=60*p,u=2,g=3;function b(e){const t=e.indexOf(".");if(-1===t)return 1e3*Date.parse(e);let a=e.indexOf("Z",t);-1===a&&(a=e.indexOf("+",t),-1===a&&(a=e.indexOf("-",t))),-1===a&&(a=e.length);const r=e.slice(0,t)+e.slice(a),o=Date.parse(r);let i=e.slice(t+1,a);return i.length<6?i=i.padEnd(6,"0"):i.length>6&&(i=i.slice(0,6)),1e3*o+Number(i)}function v(e,t="milliseconds"){if(null==e)return"—";const a=e<0?"-":"",r=Math.abs(e),o="milliseconds"===t?Math.round(r/l):Math.floor(r/l),i="microseconds"===t?r%l:0,n=Math.floor(o/h),s=Math.floor(o%h/p),d=Math.floor(o%p/c),b=o%c,v=e=>e.toString().padStart(u,"0"),_=e=>e.toString().padStart(g,"0"),m="microseconds"===t?`.${_(b)}${_(i)}`:`.${_(b)}`,y=`${v(s)}:${v(d)}`;return`${a}${n>0?`${v(n)}:${y}`:y}${m}`}},18988:function(e,t,a){a.a(e,(async function(e,r){try{a.r(t),a.d(t,{KNXProjectView:()=>w});var o=a(73742),i=a(59048),n=a(7616),s=a(28105),d=a(29173),l=a(86829),c=(a(62790),a(13965),a(78645),a(83379)),p=(a(32780),a(60495)),h=(a(92799),a(15724)),u=a(63279),g=a(38059),b=a(65793),v=e([l,c,p]);[l,c,p]=v.then?(await v)():v;const _="M6,13H18V11H6M3,6V8H21V6M10,18H14V16H10V18Z",m="M19,13H13V19H11V13H5V11H11V5H13V11H19V13Z",y="M18 7C16.9 7 16 7.9 16 9V15C16 16.1 16.9 17 18 17H20C21.1 17 22 16.1 22 15V11H20V15H18V9H22V7H18M2 7V17H8V15H4V7H2M11 7C9.9 7 9 7.9 9 9V15C9 16.1 9.9 17 11 17H13C14.1 17 15 16.1 15 15V9C15 7.9 14.1 7 13 7H11M11 9H13V15H11V9Z",f=new g.r("knx-project-view"),x="3.3.0";class w extends i.oi{disconnectedCallback(){super.disconnectedCallback(),this._subscribed&&(this._subscribed(),this._subscribed=void 0)}async firstUpdated(){this.knx.project?this._isGroupRangeAvailable():this.knx.loadProject().then((()=>{this._isGroupRangeAvailable(),this.requestUpdate()})),(0,u.ze)(this.hass).then((e=>{this._lastTelegrams=e})).catch((e=>{f.error("getGroupTelegrams",e),(0,d.c)("/knx/error",{replace:!0,data:e})})),this._subscribed=await(0,u.IP)(this.hass,(e=>{this.telegram_callback(e)}))}_isGroupRangeAvailable(){const e=this.knx.project?.knxproject.info.xknxproject_version??"0.0.0";f.debug("project version: "+e),this._groupRangeAvailable=(0,h.q)(e,x,">=")}telegram_callback(e){this._lastTelegrams={...this._lastTelegrams,[e.destination]:e}}_groupAddressMenu(e){const t=[];return t.push({path:y,label:this.knx.localize("project_view_menu_view_telegrams"),action:()=>{(0,d.c)(`/knx/group_monitor?destination=${e.address}`)}}),1===e.dpt?.main&&t.push({path:m,label:this.knx.localize("project_view_menu_create_binary_sensor"),action:()=>{(0,d.c)("/knx/entities/create/binary_sensor?knx.ga_sensor.state="+e.address)}}),i.dy`
      <ha-icon-overflow-menu .hass=${this.hass} narrow .items=${t}> </ha-icon-overflow-menu>
    `}_getRows(e){return e.length?Object.entries(this.knx.project.knxproject.group_addresses).reduce(((t,[a,r])=>(e.includes(a)&&t.push(r),t)),[]):Object.values(this.knx.project.knxproject.group_addresses)}_visibleAddressesChanged(e){this._visibleGroupAddresses=e.detail.groupAddresses}render(){if(!this.hass||!this.knx.project)return i.dy` <hass-loading-screen></hass-loading-screen> `;const e=this._getRows(this._visibleGroupAddresses);return i.dy`
      <hass-tabs-subpage
        .hass=${this.hass}
        .narrow=${this.narrow}
        .route=${this.route}
        .tabs=${this.tabs}
        .localizeFunc=${this.knx.localize}
      >
        ${this.knx.project.project_loaded?i.dy`${this.narrow&&this._groupRangeAvailable?i.dy`<ha-icon-button
                    slot="toolbar-icon"
                    .label=${this.hass.localize("ui.components.related-filter-menu.filter")}
                    .path=${_}
                    @click=${this._toggleRangeSelector}
                  ></ha-icon-button>`:i.Ld}
              <div class="sections">
                ${this._groupRangeAvailable?i.dy`
                      <knx-project-tree-view
                        .data=${this.knx.project.knxproject}
                        @knx-group-range-selection-changed=${this._visibleAddressesChanged}
                      ></knx-project-tree-view>
                    `:i.Ld}
                <ha-data-table
                  class="ga-table"
                  .hass=${this.hass}
                  .columns=${this._columns(this.narrow,this.hass.language)}
                  .data=${e}
                  .hasFab=${!1}
                  .searchLabel=${this.hass.localize("ui.components.data-table.search")}
                  .clickable=${!1}
                ></ha-data-table>
              </div>`:i.dy` <ha-card .header=${this.knx.localize("attention")}>
              <div class="card-content">
                <p>${this.knx.localize("project_view_upload")}</p>
              </div>
            </ha-card>`}
      </hass-tabs-subpage>
    `}_toggleRangeSelector(){this.rangeSelectorHidden=!this.rangeSelectorHidden}constructor(...e){super(...e),this.rangeSelectorHidden=!0,this._visibleGroupAddresses=[],this._groupRangeAvailable=!1,this._lastTelegrams={},this._columns=(0,s.Z)(((e,t)=>({address:{filterable:!0,sortable:!0,title:this.knx.localize("project_view_table_address"),flex:1,minWidth:"100px"},name:{filterable:!0,sortable:!0,title:this.knx.localize("project_view_table_name"),flex:3},dpt:{sortable:!0,filterable:!0,title:this.knx.localize("project_view_table_dpt"),flex:1,minWidth:"82px",template:e=>e.dpt?i.dy`<span style="display:inline-block;width:24px;text-align:right;"
                  >${e.dpt.main}</span
                >${e.dpt.sub?"."+e.dpt.sub.toString().padStart(3,"0"):""} `:""},lastValue:{filterable:!0,title:this.knx.localize("project_view_table_last_value"),flex:2,template:e=>{const t=this._lastTelegrams[e.address];if(!t)return"";const a=b.f3.payload(t);return null==t.value?i.dy`<code>${a}</code>`:i.dy`<div title=${a}>
            ${b.f3.valueWithUnit(this._lastTelegrams[e.address])}
          </div>`}},updated:{title:this.knx.localize("project_view_table_updated"),flex:1,showNarrow:!1,template:e=>{const t=this._lastTelegrams[e.address];if(!t)return"";const a=`${b.f3.dateWithMilliseconds(t)}\n\n${t.source} ${t.source_name}`;return i.dy`<div title=${a}>
            ${(0,p.G)(new Date(t.timestamp),this.hass.locale)}
          </div>`}},actions:{title:"",minWidth:"72px",type:"overflow-menu",template:e=>this._groupAddressMenu(e)}})))}}w.styles=i.iv`
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
  `,(0,o.__decorate)([(0,n.Cb)({type:Object})],w.prototype,"hass",void 0),(0,o.__decorate)([(0,n.Cb)({attribute:!1})],w.prototype,"knx",void 0),(0,o.__decorate)([(0,n.Cb)({type:Boolean,reflect:!0})],w.prototype,"narrow",void 0),(0,o.__decorate)([(0,n.Cb)({type:Object})],w.prototype,"route",void 0),(0,o.__decorate)([(0,n.Cb)({type:Array,reflect:!1})],w.prototype,"tabs",void 0),(0,o.__decorate)([(0,n.Cb)({type:Boolean,reflect:!0,attribute:"range-selector-hidden"})],w.prototype,"rangeSelectorHidden",void 0),(0,o.__decorate)([(0,n.SB)()],w.prototype,"_visibleGroupAddresses",void 0),(0,o.__decorate)([(0,n.SB)()],w.prototype,"_groupRangeAvailable",void 0),(0,o.__decorate)([(0,n.SB)()],w.prototype,"_subscribed",void 0),(0,o.__decorate)([(0,n.SB)()],w.prototype,"_lastTelegrams",void 0),w=(0,o.__decorate)([(0,n.Mo)("knx-project-view")],w),r()}catch(_){r(_)}}))}};
//# sourceMappingURL=2669.b34d245bf91b6c5a.js.map