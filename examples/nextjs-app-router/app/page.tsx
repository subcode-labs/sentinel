import { performSecureTask } from './actions';

export default function Page() {
  return (
    <main style={{ padding: '2rem', fontFamily: 'system-ui' }}>
      <h1>Sentinel + Next.js App Router</h1>
      <p>
        This example demonstrates <strong>Just-In-Time (JIT) Secret Access</strong> in a Server Action.
      </p>
      
      <div style={{ border: '1px solid #ccc', padding: '1rem', borderRadius: '8px', maxWidth: '400px' }}>
        <h3>Process Refund</h3>
        <p style={{ fontSize: '0.9rem', color: '#666' }}>
          This action requires the <code>stripe_api_key</code>. 
          Sentinel will audit this request and may require approval.
        </p>
        
        <form action={performSecureTask}>
          <div style={{ marginBottom: '1rem' }}>
            <label htmlFor="reason" style={{ display: 'block', marginBottom: '0.5rem' }}>
              Reason for Refund:
            </label>
            <input 
              id="reason"
              type="text" 
              name="reason" 
              placeholder="e.g. Customer unsatisfied" 
              required
              style={{ width: '100%', padding: '0.5rem' }}
            />
          </div>
          
          <button 
            type="submit"
            style={{ 
              background: '#000', 
              color: '#fff', 
              padding: '0.5rem 1rem', 
              border: 'none', 
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            Process Securely
          </button>
        </form>
      </div>
    </main>
  );
}
