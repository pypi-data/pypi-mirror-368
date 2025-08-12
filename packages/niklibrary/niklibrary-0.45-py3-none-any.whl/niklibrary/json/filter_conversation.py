import json
from datetime import datetime, timezone


def unix_to_readable(timestamp):
    if timestamp:
        # Convert Unix timestamp to human-readable format (if it's a valid number)
        return datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    return None

def clean_json(input_file, output_file):
    # Open and load the input JSON file
    with open(input_file, 'r') as f:
        data = json.load(f)

    # Function to clean up each item in the JSON data
    def clean_item(item):
        cleaned_item = {
            'title': item.get('title', ''),
            'create_time': unix_to_readable(item.get('create_time', None)),
            'update_time': unix_to_readable(item.get('update_time', None)),
            'messages': []
        }

        # Clean the message part
        for key, message_data in item.get('mapping', {}).items():
            message = message_data.get('message', {})
            if message is None:
                continue
            author = message.get('author', {})
            content = message.get('content', {})

            if content is None:
                continue

            parts = content.get('parts', [])
            if len(parts) == 0 or (len(parts) == 1 and str(parts[0]).__eq__("")):
                continue

            cleaned_message = {
                'message': message.get('id', ''),
                'author': author.get('role', ''),
                'content': content.get('parts', [])
            }
            cleaned_item['messages'].append(cleaned_message)

        return cleaned_item

    # Process each item in the data
    cleaned_data = [clean_item(item) for item in data]

    # Write the cleaned data to a new JSON file
    with open(output_file, "w") as file:
        json_str = json.dumps(cleaned_data, indent=4, sort_keys=True)
        file.write(json_str)


# Run the cleanup function
clean_json('test.json', 'cleaned_output.json')

print(f"Cleaned JSON data exported to cleaned_output.json")
