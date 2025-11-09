import 'react-native-url-polyfill/auto';
import { createClient } from '@supabase/supabase-js';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Supabase configuration
const SUPABASE_URL = 'https://xmyjprtuztwqqovonrzb.supabase.co';
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhteWpwcnR1enR3cXFvdm9ucnpiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI2NTY2NTQsImV4cCI6MjA3ODIzMjY1NH0.sC1hue1SeB5iJJypKKkVHcQ5Gup7ckKX-yP79tUN9Ek';

const supabase = createClient(SUPABASE_URL, SUPABASE_KEY, {
  auth: {
    storage: AsyncStorage,
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: false,
  },
});

// Transform Supabase customer data to app format
const transformCustomer = (supabaseCustomer) => {
  return {
    id: supabaseCustomer.customer_id,
    name: supabaseCustomer.name || supabaseCustomer.customer_id,
    accountNumber: '****' + Math.floor(Math.random() * 10000).toString().padStart(4, '0'),
    phoneNumber: '(555) XXX-XXXX', // Placeholder
    plan: 'Magenta', // Default, can be extracted from sales_context
    status: 'Standard',
    accountAge: 'New', // Placeholder
    monthlyBill: '$70.00', // Placeholder
    dataUsage: 'N/A',
    deviceModel: 'Unknown',
    lastPayment: 'N/A',
    nextBillDate: 'N/A',
    loyaltyPoints: 0,
    // Add the extracted profile data
    personalDetails: supabaseCustomer.personal_details || [],
    professionalDetails: supabaseCustomer.professional_details || [],
    salesContext: supabaseCustomer.sales_context || [],
  };
};

// Get a random customer from Supabase
export const getRandomCustomer = async () => {
  try {
    const { data, error } = await supabase
      .from('customers')
      .select('*')
      .order('updated_at', { ascending: false });

    if (error) {
      console.error('Error fetching customers:', error);
      return getFallbackCustomer();
    }

    if (!data || data.length === 0) {
      console.log('No customers found in database');
      return getFallbackCustomer();
    }

    // Get random customer
    const randomIndex = Math.floor(Math.random() * data.length);
    return transformCustomer(data[randomIndex]);

  } catch (error) {
    console.error('Error in getRandomCustomer:', error);
    return getFallbackCustomer();
  }
};

// Get customer by ID from Supabase
export const getCustomerById = async (customer_id) => {
  try {
    const { data, error } = await supabase
      .from('customers')
      .select('*')
      .eq('customer_id', customer_id)
      .single();

    if (error || !data) {
      console.error('Error fetching customer:', error);
      return null;
    }

    return transformCustomer(data);

  } catch (error) {
    console.error('Error in getCustomerById:', error);
    return null;
  }
};

// Get all customers from Supabase
export const getAllCustomers = async () => {
  try {
    const { data, error } = await supabase
      .from('customers')
      .select('*')
      .order('updated_at', { ascending: false });

    if (error) {
      console.error('Error fetching customers:', error);
      return [];
    }

    return data.map(transformCustomer);

  } catch (error) {
    console.error('Error in getAllCustomers:', error);
    return [];
  }
};

// Fallback customer for when Supabase is unavailable or empty
const getFallbackCustomer = () => {
  return {
    id: 'demo_user',
    name: 'Demo Customer',
    accountNumber: '****0000',
    phoneNumber: '(555) 000-0000',
    plan: 'Magenta',
    status: 'Standard',
    accountAge: 'New',
    monthlyBill: '$70.00',
    dataUsage: 'N/A',
    deviceModel: 'Unknown',
    lastPayment: 'N/A',
    nextBillDate: 'N/A',
    loyaltyPoints: 0,
    personalDetails: ['No customer data available'],
    professionalDetails: [],
    salesContext: ['Run a sales call to generate customer profile'],
  };
};

