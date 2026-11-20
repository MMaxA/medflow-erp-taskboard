import {useEffect,useMemo,useState} from 'react';
import {Alert,Avatar,Box,Button,Card,Chip,CircularProgress,Dialog,DialogActions,DialogContent,DialogTitle,IconButton,MenuItem,TextField,Typography} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import EditOutlinedIcon from '@mui/icons-material/EditOutlined';
import SearchIcon from '@mui/icons-material/Search';
import {api} from './api';
import type {Project,Task,User} from './api';

const columns=[
 {status:'Новая',title:'К выполнению',color:'#64748b',bg:'#f1f5f9'},
 {status:'В работе',title:'В работе',color:'#2563eb',bg:'#eff6ff'},
 {status:'На проверке',title:'На проверке',color:'#d97706',bg:'#fffbeb'},
 {status:'Выполнена',title:'Завершено',color:'#16a34a',bg:'#f0fdf4'},
];
const priorities=[{value:'Низкий',color:'default' as const},{value:'Средний',color:'info' as const},{value:'Высокий',color:'warning' as const},{value:'Критический',color:'error' as const}];
const blank={title:'',project_code:'',assignee:'',due_date:'',status:'Новая',priority:'Средний'};
type Props={tasks:Task[];projects:Project[];currentUser:User;onChanged:()=>Promise<void>};
export default function TasksBoard({tasks,projects,currentUser,onChanged}:Props){
 const [users,setUsers]=useState<User[]>([]),[dialog,setDialog]=useState(false),[editing,setEditing]=useState<Task|null>(null),[form,setForm]=useState(blank),[saving,setSaving]=useState(false),[error,setError]=useState(''),[search,setSearch]=useState(''),[dragId,setDragId]=useState<number|null>(null);
 useEffect(()=>{api<User[]>('/api/task-assignees').then(setUsers).catch(e=>setError(e.message));},[]);
 const filtered=useMemo(()=>tasks.filter(t=>[t.title,t.code,t.assignee,t.project_code].join(' ').toLowerCase().includes(search.toLowerCase())),[tasks,search]);
 function openNew(){setEditing(null);setForm({...blank,assignee:currentUser.full_name});setError('');setDialog(true)}
 function openEdit(t:Task){setEditing(t);setForm({title:t.title,project_code:t.project_code||'',assignee:t.assignee||'',due_date:t.due_date||'',status:t.status,priority:t.priority});setError('');setDialog(true)}
 async function save(){setSaving(true);setError('');try{if(!form.title.trim())throw new Error('Введите название задачи');const payload={...form,title:form.title.trim(),code:editing?.code||`TS-${Date.now().toString().slice(-7)}`};if(editing)await api(`/api/tasks/${editing.id}`,{method:'PATCH',body:JSON.stringify(payload)});else await api('/api/tasks',{method:'POST',body:JSON.stringify(payload)});setDialog(false);await onChanged()}catch(e:any){setError(e.message)}finally{setSaving(false)}}
 async function move(t:Task,status:string){if(t.status===status)return;try{await api(`/api/tasks/${t.id}/status`,{method:'PATCH',body:JSON.stringify({status})});await onChanged()}catch(e:any){setError(e.message)}}
 return <Box>
  <Box display="flex" justifyContent="space-between" alignItems={{xs:'stretch',sm:'center'}} gap={2} flexWrap="wrap" mb={2}>
   <Box><Typography variant="h5" fontWeight={800}>Задачи и поручения</Typography><Typography color="text.secondary" fontSize={13}>Kanban-доска · {tasks.length} задач</Typography></Box>
   <Box display="flex" gap={1} flexWrap="wrap"><TextField size="small" placeholder="Поиск задач..." value={search} onChange={e=>setSearch(e.target.value)} InputProps={{startAdornment:<SearchIcon sx={{mr:1,color:'text.secondary'}}/>}}/><Button variant="contained" startIcon={<AddIcon/>} onClick={openNew}>Новая задача</Button></Box>
  </Box>
  {error&&<Alert severity="error" sx={{mb:2}} onClose={()=>setError('')}>{error}</Alert>}
  <Box sx={{display:'grid',gridTemplateColumns:{xs:'1fr',sm:'repeat(2,minmax(260px,1fr))',xl:'repeat(4,minmax(230px,1fr))'},gap:2,alignItems:'start'}}>
   {columns.map(col=>{const items=filtered.filter(t=>t.status===col.status);return <Box key={col.status} onDragOver={e=>e.preventDefault()} onDrop={()=>{const t=tasks.find(x=>x.id===dragId);if(t)void move(t,col.status);setDragId(null)}} sx={{background:col.bg,borderRadius:3,p:1.5,minHeight:350,borderTop:`4px solid ${col.color}`}}>
    <Box display="flex" justifyContent="space-between" alignItems="center" mb={1.5}><Typography fontWeight={800} fontSize={14} color={col.color}>{col.title}</Typography><Chip size="small" label={items.length} sx={{fontWeight:800,bgcolor:'#fff'}}/></Box>
    <Box display="grid" gap={1.2}>
     {items.map(t=><Card key={t.id} draggable onDragStart={()=>setDragId(t.id)} onDragEnd={()=>setDragId(null)} sx={{p:1.6,borderRadius:2,cursor:'grab',border:'1px solid #e6eaf0','&:hover':{boxShadow:3,transform:'translateY(-1px)'},transition:'all .15s',opacity:dragId===t.id ? 0.5 : 1}}>
      <Box display="flex" justifyContent="space-between" alignItems="flex-start" gap={1}><Typography fontSize={10} color="text.secondary" fontWeight={700}>{t.code}</Typography><IconButton size="small" onClick={()=>openEdit(t)} aria-label="Редактировать задачу"><EditOutlinedIcon sx={{fontSize:17}}/></IconButton></Box>
      <Typography fontWeight={750} fontSize={13} lineHeight={1.45} mb={1}>{t.title}</Typography>
      <Box display="flex" gap={.6} flexWrap="wrap" mb={1.2}><Chip size="small" label={t.priority} color={priorities.find(p=>p.value===t.priority)?.color||'default'} sx={{height:22,fontSize:10,fontWeight:700}}/>{t.project_code&&<Chip size="small" label={projects.find(p=>p.code===t.project_code)?.name||t.project_code} variant="outlined" sx={{height:22,maxWidth:'100%',fontSize:10}}/>}</Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" gap={1}><Box display="flex" alignItems="center" gap={.7} minWidth={0}><Avatar sx={{width:25,height:25,fontSize:11,bgcolor:'#dbeafe',color:'#1d4ed8'}}>{(t.assignee||'?').slice(0,1)}</Avatar><Typography fontSize={10} color="text.secondary" noWrap>{t.assignee||'Не назначен'}</Typography></Box><Typography fontSize={10} color={t.due_date&&t.due_date<new Date().toISOString().slice(0,10)&&t.status!=='Выполнена'?'error.main':'text.secondary'}>{t.due_date||'Без срока'}</Typography></Box>
      <Box mt={1.2} pt={1} borderTop="1px solid #edf0f4"><TextField select fullWidth size="small" value={t.status} onChange={e=>move(t,e.target.value)} sx={{'& .MuiInputBase-root':{fontSize:11,bgcolor:'#fff'},'& .MuiSelect-select':{py:.7}}}>{columns.map(c=><MenuItem key={c.status} value={c.status}>{c.title}</MenuItem>)}</TextField></Box>
     </Card>)}
     {items.length===0&&<Box sx={{border:'1px dashed #cbd5e1',borderRadius:2,p:2,textAlign:'center',color:'#94a3b8',fontSize:12}}>Перетащите сюда задачу</Box>}
    </Box>
   </Box>})}
  </Box>
  <Dialog open={dialog} onClose={()=>!saving&&setDialog(false)} fullWidth maxWidth="sm"><DialogTitle>{editing?'Редактировать задачу':'Создать задачу'}</DialogTitle><DialogContent>
   <TextField fullWidth required margin="normal" label="Название задачи" value={form.title} onChange={e=>setForm({...form,title:e.target.value})}/>
   <TextField fullWidth select margin="normal" label="Проект / контракт" value={form.project_code} onChange={e=>setForm({...form,project_code:e.target.value})}><MenuItem value="">Без привязки к проекту</MenuItem>{projects.map(p=><MenuItem key={p.code} value={p.code}>{p.code} — {p.name}</MenuItem>)}</TextField>
   <TextField fullWidth select margin="normal" label="Исполнитель" value={form.assignee} onChange={e=>setForm({...form,assignee:e.target.value})}><MenuItem value="">Не назначен</MenuItem>{users.map(u=><MenuItem key={u.id} value={u.full_name}>{u.full_name} · {u.role}</MenuItem>)}</TextField>
   <TextField fullWidth select margin="normal" label="Приоритет" value={form.priority} onChange={e=>setForm({...form,priority:e.target.value})}>{priorities.map(p=><MenuItem key={p.value} value={p.value}>{p.value}</MenuItem>)}</TextField>
   <TextField fullWidth type="date" margin="normal" label="Срок выполнения" InputLabelProps={{shrink:true}} value={form.due_date} onChange={e=>setForm({...form,due_date:e.target.value})}/>
   <TextField fullWidth select margin="normal" label="Статус" value={form.status} onChange={e=>setForm({...form,status:e.target.value})}>{columns.map(c=><MenuItem key={c.status} value={c.status}>{c.title}</MenuItem>)}</TextField>
   {error&&<Alert severity="error" sx={{mt:1}}>{error}</Alert>}
  </DialogContent><DialogActions><Button onClick={()=>setDialog(false)} disabled={saving}>Отмена</Button><Button variant="contained" onClick={save} disabled={saving}>{saving?<CircularProgress size={18}/>:editing?'Сохранить':'Создать задачу'}</Button></DialogActions></Dialog>
 </Box>
}
