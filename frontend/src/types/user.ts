export interface User {
  id: string;
  email: string;
  username: string;
  full_name?: string;
  role: UserRole;
  organization_id?: string;
  subscription_tier: string;
  subscription_status: string;
  is_active: boolean;
  is_verified: boolean;
  preferences: UserPreferences;
  created_at: string;
  updated_at?: string;
  last_login?: string;
  gdpr_consent: boolean;
  data_retention_consent: boolean;
}

export enum UserRole {
  ADMIN = 'admin',
  DATA_SCIENTIST = 'data_scientist',
  ML_ENGINEER = 'ml_engineer',
  BUSINESS_ANALYST = 'business_analyst',
  VIEWER = 'viewer',
}

export interface UserPreferences {
  theme?: string;
  language?: string;
  timezone?: string;
  notification_preferences?: NotificationPreferences;
  dashboard_layout?: Record<string, any>;
  alert_preferences?: AlertPreferences;
}

export interface NotificationPreferences {
  email: boolean;
  slack: boolean;
  webhook: boolean;
}

export interface AlertPreferences {
  drift_alerts: boolean;
  performance_alerts: boolean;
  compliance_alerts: boolean;
}

export interface UserSubscription {
  tier: string;
  status: string;
  current_period_start?: string;
  current_period_end?: string;
  limits: SubscriptionLimits;
  usage: SubscriptionUsage;
}

export interface SubscriptionLimits {
  max_models: number;
  max_users: number;
  retention_days: number;
}

export interface SubscriptionUsage {
  models_count: number;
  users_count: number;
  storage_used_gb: number;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  username: string;
  password: string;
  full_name?: string;
  role?: UserRole;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface PasswordChangeRequest {
  current_password: string;
  new_password: string;
}

export interface PasswordResetRequest {
  email: string;
}

export interface PasswordResetConfirmRequest {
  token: string;
  new_password: string;
} 