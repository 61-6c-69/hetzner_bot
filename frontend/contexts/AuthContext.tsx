import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useRouter } from 'next/router';
import Cookies from 'js-cookie';
import { endpoints } from '@/services/api';
import type { User, AuthContextType } from '@/types';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);
    const router = useRouter();

    useEffect(() => {
        checkAuth();
    }, []);

    const login = async (token: string) => {
        Cookies.set('token', token, { expires: 30 });
        await checkAuth();
        router.push('/dashboard');
    };

    const logout = () => {
        Cookies.remove('token');
        setUser(null);
        router.push('/auth/login');
    };

    const checkAuth = async () => {
        try {
            const token = Cookies.get('token');
            if (!token) {
                setLoading(false);
                return;
            }

            const { data } = await endpoints.user.me();
            setUser(data);
        } catch (error) {
            console.error('Auth check failed:', error);
            logout();
        } finally {
            setLoading(false);
        }
    };

    const refreshUser = async () => {
        try {
            const { data } = await endpoints.user.me();
            setUser(data);
        } catch (error) {
            console.error('Failed to refresh user:', error);
        }
    };

    const isAdmin = () => {
        return user?.role === 'admin';
    };

    return (
        <AuthContext.Provider value={{ user, login, logout, loading, isAdmin, refreshUser }}>
            {!loading && children}
        </AuthContext.Provider>
    );
}

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}; 