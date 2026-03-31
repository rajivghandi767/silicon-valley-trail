export interface GameState {
    id: number;
    current_location: string;
    description: string;
    sequence_in_journey: number;
    cash: number;
    award_miles: number;
    morale: number;
    bugs: number;
    days_remaining: number;
    is_game_over: boolean;
    is_victory: boolean;
    status_summary: string;
}
