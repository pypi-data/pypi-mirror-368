ALL_COLUMNS_FRAGMENT = f'''
                                column {{ title id type }}
                        
                        ... on TextValue{{
                            text
                        }}
                        ... on DateValue{{
                            date
                        }}
                        ... on StatusValue{{
                            label
                        }}
                        ... on PeopleValue{{
                            persons_and_teams{{
                            id
                            kind
                            }}
                        }}
                        ... on DropdownValue{{
                            text
                            values{{
                            label
                            id
                            }}
                            value
                        }}
                        ... on TimelineValue{{
                            from
                            to
                        }}
                        ... on LinkValue{{
                            url
                            url_text
                        }}
                        
                        ... on NumbersValue{{
                            id 
                            number
                                    text
                            
                        }}
                        ... on FormulaValue {{
                            value
                            id
                            
                        }}
                        ... on DocValue {{
                            file{{
                            doc{{
                                url
                            }}
                            }}
                        }}
                        ... on CheckboxValue {{
                            checked
                        }}
                        ... on PhoneValue {{
                            id
                            country_short_name
                            phone
                        }}
                        ... on WorldClockValue {{
                            text
                            timezone
                            
                        }}
                        ... on LocationValue {{
                            address
                            lat
                            lng
                            
                        }}
                        ... on CountryValue {{
                            country{{
                            name
                            code
                            }}
                        }}
                        ... on DependencyValue {{
                            linked_item_ids
                        }}
                        ... on EmailValue {{
                            email
                            text
                        }}
                        ... on HourValue {{
                            minute
                            hour
                        }}
                        ... on RatingValue {{
                            rating
                            
                        }}
                        ... on TagsValue {{
                            tag_ids
                            text
                            tags {{
                            id
                            name
                            }}
                        }}
                        ... on TimeTrackingValue{{
                            running
                            history{{
                            created_at
                            started_at
                            ended_at
                            }}
                        }}
                        ... on CreationLogValue {{
                            created_at
                            creator{{
                            id
                            }}
                        }}
                        ... on ColorPickerValue {{
                            color
                            updated_at
                        }}
                        ... on LastUpdatedValue {{
                            updated_at
                            value
                        }}
                        ... on ItemIdValue {{
                            value
                            text
                        }}
                        ... on VoteValue {{
                            vote_count
                            voter_ids
                        }}
                        ... on ButtonValue {{
                            color
                            label
                        }}
                        ... on MirrorValue {{
                            display_value
                            id
                        }}
                        ... on FileValue {{
                            id
                            value
                        }}
                        ... on FormulaValue {{
                            value
                            id
                        }}
                        ... on DocValue {{
                            file{{
                            doc{{
                                id
                            }}
                            }}
                        
                        }}
                        ... on LongTextValue{{
                            text
                        }}
                        
                        ... on TimeTrackingValue{{
                            running
                            history{{
                            created_at
                            started_user_id
                            started_at
                            ended_at
                            ended_user_id
                            }}
                        }}
                        ... on BoardRelationValue{{
                            linked_items{{
                                id
                                name
                                board{{
                                  name
                                  id
                                }}
                            }}
                            linked_item_ids
                        }}
                        
        '''
        
        
        
