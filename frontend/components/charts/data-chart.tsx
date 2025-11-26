"use client";

import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";

interface ChartProps {
    data: any[];
    config: {
        type: string;
        x_axis?: string;
        y_axis?: string;
        series?: string;
    };
}

export function DataChart({ data, config }: ChartProps) {
    if (!data || data.length === 0) {
        return (
            <div className="flex items-center justify-center h-64 bg-gray-50 rounded-lg border-2 border-dashed">
                <p className="text-gray-500">No data to display</p>
            </div>
        );
    }

    const chartData = data.map((row) => {
        const item: any = {};
        Object.keys(row).forEach((key) => {
            item[key] = row[key];
        });
        return item;
    });

    if (config.type === "bar") {
        return (
            <ResponsiveContainer width="100%" height={400}>
                <BarChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey={config.x_axis || Object.keys(data[0])[0]} />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey={config.y_axis || Object.keys(data[0])[1]} fill="#8884d8" />
                </BarChart>
            </ResponsiveContainer>
        );
    }

    if (config.type === "line") {
        return (
            <ResponsiveContainer width="100%" height={400}>
                <LineChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey={config.x_axis || Object.keys(data[0])[0]} />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey={config.y_axis || Object.keys(data[0])[1]} stroke="#8884d8" />
                </LineChart>
            </ResponsiveContainer>
        );
    }

    // Default to table
    return (
        <div className="overflow-auto max-h-96">
            <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50 sticky top-0">
                    <tr>
                        {Object.keys(data[0]).map((key) => (
                            <th
                                key={key}
                                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                            >
                                {key}
                            </th>
                        ))}
                    </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                    {data.map((row, idx) => (
                        <tr key={idx}>
                            {Object.values(row).map((value: any, i) => (
                                <td key={i} className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                    {value?.toString() || "-"}
                                </td>
                            ))}
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}
