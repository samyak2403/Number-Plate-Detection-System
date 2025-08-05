class StateMapper:
    def __init__(self):
        # Mapping registration codes to locations (simplified example)
        self.mapping = {
            # India
            'AP': {'state': 'Andhra Pradesh', 'district': 'Various'},
            'AR': {'state': 'Arunachal Pradesh', 'district': 'Various'},
            'AS': {'state': 'Assam', 'district': 'Various'},
            'BR': {'state': 'Bihar', 'district': 'Various'},
            'CG': {'state': 'Chhattisgarh', 'district': 'Various'},
            'GA': {'state': 'Goa', 'district': 'Various'},
            'GJ': {'state': 'Gujarat', 'district': 'Various'},
            'HR': {'state': 'Haryana', 'district': 'Various'},
            'HP': {'state': 'Himachal Pradesh', 'district': 'Various'},
            'JK': {'state': 'Jammu and Kashmir', 'district': 'Various'},
            'JH': {'state': 'Jharkhand', 'district': 'Various'},
            'KA': {'state': 'Karnataka', 'district': 'Various'},
            'KL': {'state': 'Kerala', 'district': 'Various'},
            'MP': {'state': 'Madhya Pradesh', 'district': 'Various'},
            'MH': {'state': 'Maharashtra', 'district': 'Various'},
            'MN': {'state': 'Manipur', 'district': 'Various'},
            'ML': {'state': 'Meghalaya', 'district': 'Various'},
            'MZ': {'state': 'Mizoram', 'district': 'Various'},
            'NL': {'state': 'Nagaland', 'district': 'Various'},
            'OR': {'state': 'Odisha', 'district': 'Various'},
            'PB': {'state': 'Punjab', 'district': 'Various'},
            'RJ': {'state': 'Rajasthan', 'district': 'Various'},
            'SK': {'state': 'Sikkim', 'district': 'Various'},
            'TN': {'state': 'Tamil Nadu', 'district': 'Various'},
            'TS': {'state': 'Telangana', 'district': 'Various'},
            'TR': {'state': 'Tripura', 'district': 'Various'},
            'UP': {'state': 'Uttar Pradesh', 'district': 'Various'},
            'UK': {'state': 'Uttarakhand', 'district': 'Various'},
            'WB': {'state': 'West Bengal', 'district': 'Various'},
            # Example for other countries
            'US': {'state': 'United States', 'district': 'Various'},
            'CA': {'state': 'Canada', 'district': 'Various'},
            # Add more countries and codes here
        }

    def get_location_info(self, reg_code):
        # Extract state code from plate (first two characters)
        code = reg_code[:2]
        return self.mapping.get(code, {'state': 'Unknown', 'district': 'Unknown'})

