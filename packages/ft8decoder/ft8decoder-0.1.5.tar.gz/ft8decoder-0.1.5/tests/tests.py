from classes import MessageProcessor, Packet

with open("data.txt", 'r') as f:
    test_data = f.readlines()

test_data = [message.split("~")[-1] for message in test_data]
test_data = ["".join(message)[2:-1] for message in test_data]

packet_list = [Packet(snr=0, delta_time=0.0, frequency=0, message=message, schema=0, program="", packet_type=1)
               for message in test_data]

for pack in packet_list:
    print(pack.message)

processor = MessageProcessor()
processor.organize_messages(packet_list, 0)
print(processor.convo_dict)
print(processor.cqs)
print(processor.misc_comms)
processor.to_json()