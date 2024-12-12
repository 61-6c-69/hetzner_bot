import { Server } from '@/types';
import { useAuth } from '@/hooks/useAuth';

interface Props {
  server: Server;
  onUpdate: () => void;
}

export default function ServerCard({ server, onUpdate }: Props) {
  const { token } = useAuth();

  const handlePowerAction = async (action: 'on' | 'off') => {
    try {
      await fetch(`/api/servers/${server.id}/power`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ action })
      });
      onUpdate();
    } catch (error) {
      console.error('Failed to change power state:', error);
    }
  };

  const handleChangeIP = async () => {
    try {
      await fetch(`/api/servers/${server.id}/ip`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      onUpdate();
    } catch (error) {
      console.error('Failed to change IP:', error);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-xl font-semibold mb-4">{server.name}</h3>
      <div className="space-y-2">
        <p>IP: {server.ip}</p>
        <p>وضعیت: {server.status}</p>
        <p>سیستم عامل: {server.os}</p>
      </div>
      <div className="mt-4 space-x-2 rtl:space-x-reverse">
        <button
          onClick={() => handlePowerAction(server.status === 'running' ? 'off' : 'on')}
          className={`px-4 py-2 rounded ${
            server.status === 'running' 
              ? 'bg-red-600 text-white' 
              : 'bg-green-600 text-white'
          }`}
        >
          {server.status === 'running' ? 'خاموش کردن' : 'روشن کردن'}
        </button>
        <button
          onClick={handleChangeIP}
          className="px-4 py-2 bg-blue-600 text-white rounded"
        >
          تغییر IP
        </button>
      </div>
    </div>
  );
} 