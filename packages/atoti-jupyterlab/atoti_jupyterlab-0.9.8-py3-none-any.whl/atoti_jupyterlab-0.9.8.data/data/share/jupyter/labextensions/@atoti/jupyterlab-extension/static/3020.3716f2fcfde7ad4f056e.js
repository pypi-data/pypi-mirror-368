"use strict";(self.webpackChunk_atoti_jupyterlab_extension=self.webpackChunk_atoti_jupyterlab_extension||[]).push([[3020],{33020:(e,t,r)=>{r.r(t),r.d(t,{default:()=>u});var n=r(74389),i=r(40570),a=r(74667),o=r(31529),c=r(93345),s=r(33349);const u=e=>{const t=(0,c.useRef)(null),r=(0,c.useRef)(null),u=(0,c.useRef)(null),[l,d]=(0,c.useState)(0),p=(0,o.isArray)(e.disabled)&&!e.disabled[1];return(0,c.useEffect)((()=>{if(p){const e=Array.from(t.current?.querySelectorAll(".ant-picker-input > input")??[]);r.current=e[0],u.current=e[1];const n=()=>d(0);r.current?.addEventListener("focus",n);const i=()=>d(1);return u.current?.addEventListener("focus",i),()=>{r.current?.removeEventListener("focus",n),u.current?.removeEventListener("focus",i)}}return d(0),()=>{}}),[p]),(0,n.Y)("div",{"aria-label":"Date picker",ref:t,css:i.css`
        position: relative;
        .ant-picker-active-bar {
          opacity: 1;
        }
        .ant-picker-dropdown {
          left: 0% !important;
          top: 32px !important;
          opacity: 1 !important;
          transform: scale(1) !important;
        }
      `,children:(0,n.Y)(a.ConfigProvider,{theme:{components:{DatePicker:{boxShadowSecondary:"unset",motionDurationMid:"unset",sizePopupArrow:0}}},children:(0,n.Y)(s.DateRangePicker,{...e,open:!0,onCalendarChange:(...t)=>{if(p){if(!t[0])return d(0),void r.current?.focus();{const e=(l+1)%2;d(e),(0===e?r:u).current?.focus()}}e.onCalendarChange?.(...t)},activePickerIndex:l,getPopupContainer:e=>t.current??e,panelRender:e=>(0,n.FD)("div",{css:{display:"flex",flexDirection:"column"},children:[e,(0,n.Y)(s.LegendForDatesWithData,{style:{alignSelf:"flex-end"}})]})})})})}}}]);