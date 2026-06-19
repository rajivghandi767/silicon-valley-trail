export type GameAction = 
    | 'rest' 
    | 'code' 
    | 'mentor' 
    | 'travel_ferry' 
    | 'travel_flight';

export interface GameState {
    current_location: string;
    description: string;
    sequence_in_journey: number;
    total_stops: number;
    cash: number;
    award_miles: number;
    morale: number;
    bugs: number;
    days_remaining: number;
    is_won: boolean;
    is_lost: boolean;
    status_summary: string;
    message?: string;
    stat_statuses: {
        days: "critical" | "good";
        cash: "critical" | "good";
        miles: "default" | "blue";
        morale: "critical" | "good";
        bugs: "critical" | "warning" | "good";
    };
}