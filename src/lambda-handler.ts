export interface Event {
  name?: string;
}

export async function handler(event: Event): Promise<string> {
  console.log('Event received:', JSON.stringify(event, null, 2));
  
  const name = event.name || 'World';
  const message = `Hello, \${name}!`;
  
  console.log('Response:', message);
  return message;
}