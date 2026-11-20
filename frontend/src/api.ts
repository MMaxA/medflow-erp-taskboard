const BASE=import.meta.env.VITE_API_URL||"";
export type User={id:number;email:string;full_name:string;role:string};
export type Project={id:number;code:string;name:string;customer:string;product:string;stage:string;owner:string;amount:number;probability:number;description:string;created_at:string;updated_at:string};
export type Task={id:number;code:string;title:string;project_code:string;assignee:string;due_date:string;status:string;priority:string};
export type Activity={id:number;project_code:string;actor:string;action:string;details:string;created_at:string};
export type Notification={id:number;title:string;message:string;is_read:boolean;created_at:string};
export function token(){return localStorage.getItem("mf-token")}
function readableDetail(detail:unknown):string{
 if(typeof detail==="string")return detail;
 if(Array.isArray(detail))return detail.map((item:any)=>[item.loc?.slice?.(1).join("."),item.msg].filter(Boolean).join(": ")).join("; ");
 if(detail&&typeof detail==="object")return JSON.stringify(detail);
 return "";
}
export async function api<T>(path:string,options:RequestInit={}):Promise<T>{
 const headers=new Headers(options.headers||{});
 if(options.body!==undefined)headers.set("Content-Type","application/json");
 if(token())headers.set("Authorization",`Bearer ${token()}`);
 let res:Response;
 try{res=await fetch(`${BASE}${path}`,{...options,headers})}
 catch{throw new Error(`Не удалось связаться с API (${BASE}). Проверьте, что backend запущен.`)}
 if(!res.ok){let msg=`HTTP ${res.status} ${res.statusText}`;try{const d=await res.json();msg=readableDetail(d.detail)||readableDetail(d.message)||msg}catch{};throw new Error(msg)}
 if(res.status===204)return undefined as T;
 return res.json();
}
