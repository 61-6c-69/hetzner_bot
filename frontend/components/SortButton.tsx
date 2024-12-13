import { FiChevronUp, FiChevronDown } from 'react-icons/fi';
import type { SortButtonProps } from '@/types';

export default function SortButton({ label, field, currentSort, onSort }: SortButtonProps) {
    const isActive = currentSort.field === field;

    return (
        <button
            onClick={() => onSort(field)}
            className={`inline-flex items-center space-x-1 space-x-reverse ${className}`}
        >
            <span>{label}</span>
            <div className="flex flex-col">
                <FiChevronUp
                    className={`w-3 h-3 ${
                        isActive && currentSort.order === 'asc'
                            ? 'text-blue-600'
                            : 'text-gray-400'
                    }`}
                />
                <FiChevronDown
                    className={`w-3 h-3 ${
                        isActive && currentSort.order === 'desc'
                            ? 'text-blue-600'
                            : 'text-gray-400'
                    }`}
                />
            </div>
        </button>
    );
} 