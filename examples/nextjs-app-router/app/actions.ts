'use server';

import { sentinel } from '../lib/sentinel';

/**
 * A Server Action that performs a sensitive operation.
 * It requests a secret Just-In-Time (JIT) from Sentinel.
 */
export async function performSecureTask(formData: FormData) {
  const reason = formData.get('reason') as string;
  
  if (!reason) {
    return { error: 'Reason is required' };
  }

  try {
    // 1. Request access to the secret
    // This might trigger a human approval workflow if configured in Sentinel
    console.log('[Server Action] Requesting stripe_api_key...');
    
    const access = await sentinel.requestWithPolling({
      resourceId: 'stripe_api_key',
      intent: {
        summary: 'Process Refund',
        description: `User requested refund. Reason: ${reason}`,
        task_id: `refund-${Date.now()}`
      }
    });

    if (access.status !== 'APPROVED' || !access.secret) {
      return { error: `Access denied: ${access.status}` };
    }

    // 2. Use the secret
    const stripeKey = access.secret.value;
    console.log('[Server Action] Acquired secret. Performing operation...');
    
    // Simulate Stripe API call
    // const stripe = new Stripe(stripeKey);
    // await stripe.refunds.create(...)
    
    await new Promise(resolve => setTimeout(resolve, 500)); // Mock latency

    return { success: true, message: 'Refund processed successfully (Secret accessed & validated)' };

  } catch (error) {
    console.error('Sentinel Error:', error);
    return { error: 'Failed to access secure resources' };
  }
}
