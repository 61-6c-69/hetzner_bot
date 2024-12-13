import { useState, useEffect } from 'react';
import { FiSearch } from 'react-icons/fi';
import debounce from 'lodash/debounce';

interface SearchInputProps {
    onSearch: (query: string) => void;
    placeholder?: string;
    className?: string;
}

export default function SearchInput({ onSearch, placeholder = 'جستجو...', className = '' }: SearchInputProps) {
    const [query, setQuery] = useState('');

    // Debounce search to avoid too many API calls
    const debouncedSearch = debounce((value: string) => {
        onSearch(value);
    }, 500);

    useEffect(() => {
        return () => {
            debouncedSearch.cancel();
        };
    }, []);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const value = e.target.value;
        setQuery(value);
        debouncedSearch(value);
    };

    return (
        <div className={`relative ${className}`}>
            <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
                <FiSearch className="w-5 h-5 text-gray-400" />
            </div>
            <input
                type="text"
                value={query}
                onChange={handleChange}
                placeholder={placeholder}
                className="block w-full pr-10 py-2 text-sm text-gray-900 border border-gray-300 rounded-lg bg-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
        </div>
    );
} 