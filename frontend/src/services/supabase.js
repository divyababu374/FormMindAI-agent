import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

export const isSupabaseConfigured = Boolean(
  supabaseUrl && 
  supabaseAnonKey && 
  !supabaseUrl.includes('your-supabase') && 
  !supabaseAnonKey.includes('your-anon-key')
);

// Create Supabase client instance if configured
export const supabase = isSupabaseConfigured
  ? createClient(supabaseUrl, supabaseAnonKey, {
      auth: {
        autoRefreshToken: true,
        persistSession: true,
        detectSessionInUrl: true,
      },
    })
  : null;

/**
 * Supabase Auth Service
 * Strictly handles authentication, user identity, and basic profile data.
 * No survey or analysis data is stored in Supabase.
 */
export const authService = {
  isConfigured: () => isSupabaseConfigured,

  /**
   * Triggers Supabase OAuth with Google provider.
   * Uses prompt: 'select_account' to force Google to show the account selection screen.
   */
  signInWithGoogle: async () => {
    if (!isSupabaseConfigured || !supabase) {
      throw new Error(
        'Supabase authentication is not configured. Please set VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY in your environment.'
      );
    }

    const { data, error } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: {
        redirectTo: window.location.origin,
        queryParams: {
          prompt: 'select_account',
        },
      },
    });

    if (error) throw error;
    return data;
  },

  /**
   * Signs out the current user and clears Supabase session.
   */
  signOut: async () => {
    if (isSupabaseConfigured && supabase) {
      const { error } = await supabase.auth.signOut();
      if (error) console.error('Supabase sign out error:', error);
    }
    localStorage.removeItem('formmind_token');
    localStorage.removeItem('formmind_dev_user');
  },

  /**
   * Retrieves the currently authenticated Supabase session.
   */
  getSession: async () => {
    if (!isSupabaseConfigured || !supabase) {
      return null;
    }

    const { data, error } = await supabase.auth.getSession();
    if (error) {
      console.error('Error fetching session:', error);
      return null;
    }
    return data.session;
  },

  /**
   * Retrieves the currently authenticated Supabase user.
   */
  getUser: async () => {
    if (!isSupabaseConfigured || !supabase) {
      return null;
    }

    const { data, error } = await supabase.auth.getUser();
    if (error) return null;
    return data.user;
  },

  /**
   * Listens to auth state changes (SIGN_IN, SIGN_OUT, TOKEN_REFRESHED).
   */
  onAuthStateChange: (callback) => {
    if (!isSupabaseConfigured || !supabase) {
      return { data: { subscription: { unsubscribe: () => {} } } };
    }
    return supabase.auth.onAuthStateChange(callback);
  },

  /**
   * Syncs minimal profile information in Supabase 'profiles' table.
   */
  upsertProfile: async (user) => {
    if (!isSupabaseConfigured || !supabase || !user) return;
    try {
      const profileData = {
        id: user.id,
        name: user.user_metadata?.full_name || user.email?.split('@')[0] || 'User',
        email: user.email,
        avatar_url: user.user_metadata?.avatar_url || null,
        last_login: new Date().toISOString(),
      };

      await supabase.from('profiles').upsert(profileData, { onConflict: 'id' });
    } catch (err) {
      // Non-critical profile sync logging
      console.debug('Profile table upsert info:', err.message);
    }
  },
};
