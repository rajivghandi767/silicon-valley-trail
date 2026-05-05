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
    is_won: boolean;
    is_lost: boolean;
    status_summary: string;
    message?: string;
}

export interface BugReport {
    issue_type: 'game_logic' | 'ui_bug' | 'typo' | 'other';
    user_note: string;
}
