import React, { useEffect, useState } from 'react';
import { Shield, Server, AlertTriangle, Activity, Terminal, RefreshCw, Search, Lock, Cpu } from 'lucide-react';
import { Device, SecurityEvent } from './types';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
const WS_BASE = import.meta.env.VITE_WS_BASE_URL || 'ws://127.0.0.1:8000';

export default function App() {
  const [devices, setDevices] = useState<Device[]>([]);
  const [events, setEvents] = useState<SecurityEvent[]>([]);
  const [targetIp, setTargetIp] = useState('');
  const [isScanning, setIsScanning] = useState(false);
  const [scanOutput, setScanOutput] = useState<any>(null);

  const fetchData = async () => {
    try {
      const devRes = await fetch(`${API_BASE}/api/v1/devices`);
      setDevices(await devRes.json());

      const evtRes = await fetch(`${API_BASE}/api/v1/events`);
      setEvents(await evtRes.json());
    } catch (e) {
      console.error("API connection failed:", e);
    }
  };

  useEffect(() => {
    fetchData();
    const ws = new WebSocket(`${WS_BASE}/ws/events`);
    ws.onmessage = () => fetchData();
    return () => ws.close();
  }, []);

  const handleScan = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!targetIp) return;
    setIsScanning(true);
    setScanOutput(null);

    try {
      const res = await fetch(`${API_BASE}/api/v1/scan`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ target_cidr: targetIp, start_port: 1, end_port: 1024 }),
      });
      setScanOutput(await res.json());
      fetchData();
    } catch (err) {
      alert('Scan error or unauthorized target!');
    } finally {
      setIsScanning(false);
    }
  };

  const getSeverityBadge = (severity: string) => {
    const colors: Record<string, string> = {
      CRITICAL: 'bg-red-950 text-red-400 border-red-800',
      HIGH: 'bg-orange-950 text-orange-400 border-orange-800',
      MEDIUM: 'bg-yellow-950 text-yellow-400 border-yellow-800',
      LOW: 'bg-blue-950 text-blue-400 border-blue-800',
      INFO: 'bg-slate-800 text-slate-300 border-slate-700'
    };
    return (
      <span className={`px-2 py-0.5 text-xs font-mono border rounded ${colors[severity] || colors.INFO}`}>
        {severity}
      </span>
    );
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans">
      <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Shield className="w-8 h-8 text-cyan-400" />
          <div>
            <h1 className="text-xl font-bold tracking-wider text-slate-100 uppercase">NETGUARD SOC</h1>
            <p className="text-xs font-mono text-slate-400">Enterprise Threat Monitoring Engine</p>
          </div>
        </div>
        <button onClick={fetchData} className="flex items-center gap-2 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-xs font-mono rounded border border-slate-700">
          <RefreshCw className="w-3.5 h-3.5" /> REFRESH STATE
        </button>
      </header>

      <main className="p-6 grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-4 grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-slate-900 border border-slate-800 p-4 rounded-lg flex items-center gap-4">
            <Server className="w-8 h-8 text-cyan-400" />
            <div>
              <p className="text-xs font-mono text-slate-400 uppercase">Tracked Assets</p>
              <p className="text-2xl font-bold text-slate-100">{devices.length}</p>
            </div>
          </div>
          <div className="bg-slate-900 border border-slate-800 p-4 rounded-lg flex items-center gap-4">
            <AlertTriangle className="w-8 h-8 text-red-400" />
            <div>
              <p className="text-xs font-mono text-slate-400 uppercase">Critical Events</p>
              <p className="text-2xl font-bold text-red-400">
                {events.filter(e => e.severity === 'CRITICAL' || e.severity === 'HIGH').length}
              </p>
            </div>
          </div>
          <div className="bg-slate-900 border border-slate-800 p-4 rounded-lg flex items-center gap-4">
            <Activity className="w-8 h-8 text-green-400" />
            <div>
              <p className="text-xs font-mono text-slate-400 uppercase">Engine Status</p>
              <p className="text-sm font-bold text-green-400 font-mono">ACTIVE / LISTENING</p>
            </div>
          </div>
          <div className="bg-slate-900 border border-slate-800 p-4 rounded-lg flex items-center gap-4">
            <Lock className="w-8 h-8 text-purple-400" />
            <div>
              <p className="text-xs font-mono text-slate-400 uppercase">Scope Guardrail</p>
              <p className="text-sm font-bold text-purple-400 font-mono">RFC1918 ENFORCED</p>
            </div>
          </div>
        </div>

        <div className="lg:col-span-2 space-y-6">
          <div className="bg-slate-900 border border-slate-800 rounded-lg p-5">
            <h2 className="text-sm font-mono font-bold text-cyan-400 uppercase tracking-wider mb-4 flex items-center gap-2">
              <Cpu className="w-4 h-4" /> Network Assets & Risk Exposures
            </h2>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs font-mono">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400">
                    <th className="pb-2">HOST</th>
                    <th className="pb-2">IP / MAC</th>
                    <th className="pb-2">OPEN PORTS</th>
                    <th className="pb-2">RISK</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/50">
                  {devices.map(d => (
                    <tr key={d.id} className="hover:bg-slate-800/30">
                      <td className="py-3 font-semibold text-slate-200">{d.device_name}</td>
                      <td className="py-3 text-slate-400">{d.ip_address}<br/><span className="text-[10px] text-slate-500">{d.mac_address}</span></td>
                      <td className="py-3">
                        <div className="flex flex-wrap gap-1">
                          {d.ports.map(p => (
                            <span key={p.id} className="px-1.5 py-0.5 bg-slate-800 text-cyan-300 border border-slate-700 rounded text-[10px]">
                              {p.port}
                            </span>
                          ))}
                          {d.ports.length === 0 && <span className="text-slate-600">None</span>}
                        </div>
                      </td>
                      <td className="py-3">
                        <span className={`font-bold ${d.risk_score > 50 ? 'text-red-400' : d.risk_score > 20 ? 'text-yellow-400' : 'text-green-400'}`}>
                          {d.risk_score.toFixed(0)} / 100
                        </span>
                      </td>
                    </tr>
                  ))}
                  {devices.length === 0 && (
                    <tr>
                      <td colSpan={4} className="py-4 text-center text-slate-500">No assets detected. Run telemetry agent on target machine.</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-lg p-5">
            <h2 className="text-sm font-mono font-bold text-purple-400 uppercase tracking-wider mb-4 flex items-center gap-2">
              <Search className="w-4 h-4" /> Scoped TCP Recon Engine
            </h2>
            <form onSubmit={handleScan} className="flex gap-2 mb-4">
              <input 
                type="text" 
                placeholder="Target IPv4 (e.g. 192.168.1.1)"
                value={targetIp}
                onChange={e => setTargetIp(e.target.value)}
                className="flex-1 bg-slate-950 border border-slate-700 rounded px-3 py-2 text-xs font-mono text-slate-100 focus:outline-none focus:border-purple-500"
              />
              <button 
                type="submit" 
                disabled={isScanning}
                className="bg-purple-600 hover:bg-purple-500 text-white font-mono text-xs px-4 py-2 rounded disabled:opacity-50"
              >
                {isScanning ? 'SCANNING...' : 'EXECUTE SCAN'}
              </button>
            </form>

            {scanOutput && (
              <div className="bg-slate-950 border border-slate-800 p-3 rounded font-mono text-xs space-y-2">
                <p className="text-purple-300 font-bold">Target: {scanOutput.target}</p>
                <div className="divide-y divide-slate-800">
                  {scanOutput.open_ports.map((op: any) => (
                    <div key={op.port} className="py-1 flex justify-between">
                      <span className="text-green-400">PORT {op.port} OPEN</span>
                      <span className="text-slate-400">{op.banner}</span>
                    </div>
                  ))}
                  {scanOutput.open_ports.length === 0 && <p className="text-slate-500 py-1">No open ports discovered in target scope.</p>}
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-lg p-5 flex flex-col h-full">
          <h2 className="text-sm font-mono font-bold text-red-400 uppercase tracking-wider mb-4 flex items-center gap-2">
            <Terminal className="w-4 h-4" /> Live Security Threat Stream
          </h2>
          <div className="flex-1 overflow-y-auto space-y-3 max-h-[600px] pr-2">
            {events.map(e => (
              <div key={e.id} className="bg-slate-950 border border-slate-800/80 p-3 rounded space-y-1">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    {getSeverityBadge(e.severity)}
                    <span className="text-xs font-mono font-bold text-slate-200">{e.event_type}</span>
                  </div>
                  <span className="text-[10px] font-mono text-slate-500">{new Date(e.timestamp).toLocaleTimeString()}</span>
                </div>
                <p className="text-xs text-slate-300 font-sans">{e.description}</p>
                <div className="text-[10px] font-mono text-slate-500 flex gap-4 pt-1">
                  {e.source_ip && <span>SRC: {e.source_ip}</span>}
                  {e.port && <span>PORT: {e.port}</span>}
                </div>
              </div>
            ))}
            {events.length === 0 && (
              <p className="text-center text-slate-500 py-12 text-xs font-mono">No security events logged.</p>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
