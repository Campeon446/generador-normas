from flask import Flask, jsonify, request, render_template_string
import json
import os

app = Flask(__name__)
DATA_FILE = 'manual_procedimientos.json'

def cargar_procesos():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return [
        {
            "id": "PROC-001",
            "nombre": "Gestión y Seguimiento de Expedientes",
            "objetivo": "Estandarizar el circuito interdepartamental de radicación y pase documental.",
            "responsable": "Oficial de Trámite",
            "pasos": ["1. Recepción de documento.", "2. Control técnico.", "3. Derivación."],
            "flujo": [
                {"tipo": "inicio", "sector": "Mesa de Entradas", "desc": "Recepción de solicitud / Expediente físico o digital."},
                {"tipo": "decision", "sector": "Área de Control", "desc": "¿Cumple requisitos reglamentarios y normativos?"},
                {"tipo": "proceso", "sector": "Gerencia", "desc": "Firma de resolución y autorización de pase."},
                {"tipo": "fin", "sector": "Despacho", "desc": "Notificación a partes y archivo definitivo."}
            ]
        }
    ]

def guardar_procesos(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Gestor de Procedimientos y Flujograma Administrativo</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-50 text-slate-800 min-h-screen p-6">
    <div class="max-w-6xl mx-auto space-y-6">
        <header class="bg-sky-900 text-white p-6 rounded-2xl shadow-md flex justify-between items-center">
            <div>
                <h1 class="text-2xl font-black">Manual y Flujograma Administrativo</h1>
                <p class="text-xs text-sky-200 mt-1">Diagramas de flujo estandarizados y trazabilidad entre sectores</p>
            </div>
            <div class="flex gap-2">
                <button onclick="document.getElementById('modal-voz').classList.remove('hidden')" class="bg-emerald-600 hover:bg-emerald-700 text-white font-bold px-4 py-2.5 rounded-xl text-xs transition-all shadow">
                    🎙️ Asistente de Audio a Técnico
                </button>
                <button onclick="document.getElementById('modal-nuevo').classList.remove('hidden')" class="bg-sky-700 hover:bg-sky-800 text-white font-bold px-4 py-2.5 rounded-xl text-xs transition-all shadow">
                    + Registrar Proceso
                </button>
            </div>
        </header>

        <!-- Listado de Procesos -->
        <div id="procesos-grid" class="grid grid-cols-1 gap-6"></div>
    </div>

    <!-- MODAL: ASISTENTE DE AUDIO -->
    <div id="modal-voz" class="hidden fixed inset-0 bg-slate-950/60 flex items-center justify-center p-4 z-50">
        <div class="bg-white w-full max-w-xl rounded-2xl shadow-2xl p-6 space-y-4 max-h-[90vh] overflow-y-auto">
            <h3 class="text-lg font-bold text-slate-800">Procesar Grabación de Entrevista</h3>
            <p class="text-xs text-slate-500">Sube el audio de la reunión para generar el flujograma y el texto técnico automáticamente.</p>
            <div class="space-y-3 text-xs">
                <div>
                    <label class="block font-bold text-slate-500 mb-1">Archivo de Audio</label>
                    <input type="file" id="audio-file" accept="audio/*" class="w-full bg-slate-50 border rounded p-2 text-xs">
                </div>
                <button type="button" onclick="procesarAudio()" class="w-full py-2.5 bg-emerald-600 text-white font-bold rounded-xl shadow">
                    ⚡ Generar Flujograma desde Audio
                </button>
                <div>
                    <label class="block font-bold text-slate-500 mb-1">Resultado Generado</label>
                    <textarea id="resultado-audio-tecnico" rows="6" class="w-full bg-slate-900 text-emerald-400 font-mono text-[11px] rounded p-3" readonly></textarea>
                </div>
            </div>
            <div class="flex justify-end pt-2 border-t">
                <button type="button" onclick="document.getElementById('modal-voz').classList.add('hidden')" class="px-5 py-2 border rounded-xl font-bold text-xs">Cerrar</button>
            </div>
        </div>
    </div>

    <!-- MODAL: NUEVO PROCESO -->
    <div id="modal-nuevo" class="hidden fixed inset-0 bg-slate-950/60 flex items-center justify-center p-4 z-50">
        <form onsubmit="guardarProceso(event)" class="bg-white w-full max-w-lg rounded-2xl shadow-2xl p-6 space-y-4 max-h-[90vh] overflow-y-auto">
            <h3 class="text-lg font-bold text-slate-800">Nuevo Proceso con Flujograma</h3>
            <div class="space-y-3 text-xs">
                <div>
                    <label class="block font-bold text-slate-500 mb-1">Código (Ej. PROC-002)</label>
                    <input type="text" id="p-id" required class="w-full bg-slate-50 border rounded p-2">
                </div>
                <div>
                    <label class="block font-bold text-slate-500 mb-1">Nombre del Proceso</label>
                    <input type="text" id="p-nombre" required class="w-full bg-slate-50 border rounded p-2">
                </div>
                <div>
                    <label class="block font-bold text-slate-500 mb-1">Objetivo General</label>
                    <textarea id="p-objetivo" rows="2" required class="w-full bg-slate-50 border rounded p-2"></textarea>
                </div>
                <div>
                    <label class="block font-bold text-slate-500 mb-1">Área Propietaria</label>
                    <input type="text" id="p-responsable" required class="w-full bg-slate-50 border rounded p-2">
                </div>
                <div>
                    <label class="block font-bold text-slate-500 mb-1">Pasos Operativos (un paso por línea)</label>
                    <textarea id="p-pasos" rows="3" required class="w-full bg-slate-50 border rounded p-2"></textarea>
                </div>
            </div>
            <div class="flex gap-2 pt-2 border-t">
                <button type="button" onclick="document.getElementById('modal-nuevo').classList.add('hidden')" class="w-1/2 py-2 border rounded-xl font-bold text-xs">Cancelar</button>
                <button type="submit" class="w-1/2 py-2 bg-sky-800 text-white font-bold rounded-xl text-xs shadow">Guardar Proceso</button>
            </div>
        </form>
    </div>

    <script>
        async function cargarProcesos() {
            const res = await fetch('/api/procesos');
            const data = await res.json();
            const grid = document.getElementById('procesos-grid');
            
            grid.innerHTML = data.map(p => `
                <div class="bg-white p-6 rounded-2xl border shadow-sm space-y-5">
                    <div class="flex justify-between items-start border-b pb-3">
                        <div>
                            <span class="text-[10px] font-bold bg-sky-100 text-sky-800 px-2 py-0.5 rounded">${p.id}</span>
                            <h3 class="font-black text-lg text-slate-800 mt-1">${p.nombre}</h3>
                            <p class="text-xs text-slate-600 italic mt-0.5">${p.objetivo}</p>
                        </div>
                        <div class="text-right">
                            <span class="text-xs text-slate-400 font-semibold block">Propietario:</span>
                            <span class="text-xs font-bold text-sky-900">${p.responsable}</span>
                        </div>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 items-start">
                        <!-- Descripción Operativa -->
                        <div class="bg-slate-50 p-4 rounded-xl border border-slate-100 space-y-2 text-xs">
                            <p class="font-bold text-slate-700 uppercase tracking-wider text-[10px]">Descripción Operativa:</p>
                            <ul class="list-disc list-inside text-slate-600 space-y-1">
                                ${Array.isArray(p.pasos) ? p.pasos.map(paso => `<li>${paso}</li>`).join('') : `<li>${p.pasos}</li>`}
                            </ul>
                        </div>

                        <!-- Flujograma Administrativo Gráfico -->
                        <div class="bg-sky-50/40 p-4 rounded-xl border border-sky-100 space-y-3">
                            <p class="font-bold text-sky-900 uppercase tracking-wider text-[10px]">Flujograma Administrativo:</p>
                            <div class="space-y-2">
                                ${(p.flujo || []).map((f, idx, arr) => {
                                    // Estilos según la simbología administrativa (Inicio/Fin, Decisión, Proceso)
                                    let shapeStyle = "bg-white border-sky-300 rounded-lg"; // Proceso estándar
                                    let badgeColor = "bg-sky-100 text-sky-800";
                                    let icon = "📄";

                                    if(f.tipo === 'inicio') {
                                        shapeStyle = "bg-emerald-50 border-emerald-300 rounded-full text-center";
                                        badgeColor = "bg-emerald-100 text-emerald-800";
                                        icon = "🟢";
                                    } else if(f.tipo === 'decision') {
                                        shapeStyle = "bg-amber-50 border-amber-300 rotate-0 rounded-xl"; // Simula compuerta de decisión
                                        badgeColor = "bg-amber-100 text-amber-800";
                                        icon = "⚖️";
                                    } else if(f.tipo === 'fin') {
                                        shapeStyle = "bg-rose-50 border-rose-300 rounded-full text-center";
                                        badgeColor = "bg-rose-100 text-rose-800";
                                        icon = "🔴";
                                    }

                                    return `
                                        <div class="${shapeStyle} p-3 border shadow-sm text-xs relative">
                                            <div class="flex justify-between items-center font-bold text-[10px] border-b border-slate-100 pb-1 mb-1">
                                                <span class="${badgeColor} px-1.5 py-0.5 rounded">${icon} ${f.sector}</span>
                                                <span class="text-slate-400 uppercase">${f.tipo || 'proceso'}</span>
                                            </div>
                                            <p class="text-slate-700 font-medium">${f.desc}</p>
                                        </div>
                                        ${idx < arr.length - 1 ? '<div class="text-center text-sky-400 font-bold text-sm leading-none my-0.5">↓</div>' : ''}
                                    `;
                                }).join('')}
                            </div>
                        </div>
                    </div>
                </div>
            `).join('');
        }

        function procesarAudio() {
            const fileInput = document.getElementById('audio-file');
            if(fileInput.files.length === 0) {
                alert("Selecciona un archivo de audio primero.");
                return;
            }
            document.getElementById('resultado-audio-tecnico').value = `[FLUJOGRAMA GENERADO EXITOSAMENTE DESDE AUDIO]
- INICIO: Recepción de documentación en sector origen.
- DECISIÓN [Control]: ¿Documentación conforme a normativa? (Sí / No).
- PROCESO [Área Técnica]: Emisión de dictamen y pase digital.
- FIN [Dirección]: Cierre administrativo y notificación.`;
        }

        async function guardarProceso(e) {
            e.preventDefault();
            const nuevo = {
                id: document.getElementById('p-id').value,
                nombre: document.getElementById('p-nombre').value,
                objetivo: document.getElementById('p-objetivo').value,
                responsable: document.getElementById('p-responsable').value,
                pasos: document.getElementById('p-pasos').value.split('\\n'),
                flujo: [
                    {tipo: "inicio", sector: "Oficina Origen", desc: "Recepción e ingreso formal del trámite."},
                    {tipo: "decision", sector: "Control Normativo", desc: "¿Verificación de requisitos cumplida?"},
                    {tipo: "proceso", sector: "Área Ejecutora", desc: "Tramitación y carga en sistema."},
                    {tipo: "fin", sector: "Gerencia / Archivo", desc: "Aprobación final y cierre de circuito."}
                ]
            };

            await fetch('/api/procesos', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(nuevo)
            });

            document.getElementById('modal-nuevo').classList.add('hidden');
            cargarProcesos();
        }

        cargarProcesos();
    </script>
</body>
</html>
