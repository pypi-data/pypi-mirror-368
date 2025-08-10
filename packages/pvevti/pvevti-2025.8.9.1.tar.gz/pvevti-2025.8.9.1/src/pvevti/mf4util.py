from asammdf import MDF, Signal
from pandas import DataFrame, to_timedelta, concat
from os import path

class MF4Object():
    def __init__(self, filepath):
        """
        Create an MF4 Object from the filepath provided.\n
        `MF4Object.num_channels` returns an integer of the total count of unique channels. 
        Two identically named channels from two different groups count as one channel.\n
        `MF4Object.data` returns the MDF object.\n
        `MF4Object.channel_data` returns a list of `signalOBJ`s containing properties:\n
          "Name": The channel name\n
          "Group": The integer group number\n
          "Unit": The units of the channel\n
        """
        if path.isfile(filepath) and '.mf4' in filepath.lower():
            self.data = MDF(filepath)
            channels = []
            self.channel_data = []
            for i, group in enumerate(self.data.groups):
                for channel in group.channels:
                    channels.append(channel.name)
                    unit = channel.conversion.unit if channel.conversion else ""
                    self.channel_data.append({'Name': channel.name, 'Group': i, 'Unit': unit})
            
            self.num_channels = len(list(set(channels)))
        else:
            raise ValueError("Filepath '{}' does not point to a valid MF4.".format(filepath))
    
    def get_all_channels(self):
        """
        Returns a list of channel names as strings. Does not include any other data; output is a list of `str`s, not `signalObj`s. 
        """
        return list(set([ch['Name'] for ch in self.channel_data]))
    
    def channels_by_name(self, names, only_names=False):
        """
        Given a list of `names` (or a string of one `name`), returns the `signalObj`s corresponding to each.
        If a `name` cannot be found in the MF4, it is ignored.
        If the optional `only_names` parameter is provided and `True`, returns only the formatted names of each matching channel.
        """
        if isinstance(names, str):
            names = [names]
        
        result = []
        if only_names:
            for name in names:
                result += [item['Name']+"["+item["Unit"]+"]" for item in self.channel_data if item['Name'].lower().strip() == str(name).lower().strip()]
        else:
            for name in names:
                result += [item for item in self.channel_data if item['Name'].lower().strip() == str(name).lower().strip()]
        return result
    
    def channels_by_unit(self, unit:str, only_names:bool=False):
        """
        Given a `unit` returns the `signalObj`s corresponding to each.
        If the `unit` cannot be found in the MF4, it is ignored. 
        If the optional `only_names` parameter is provided and `True`, returns only the formatted names of each matching channel.
        """
        if only_names:
            return [item['Name']+"["+item["Unit"]+"]" for item in self.channel_data if item['Unit'] == unit]
        else:
            return [item for item in self.channel_data if item['Unit'] == unit]
    
    def dataFrame(self, channels:list=[], resample:float=1.0):
        """
        Returns a pandas dataFrame object containing only the selected channels, with data resampled to the `resample` value (a frequency in units of seconds).
        """
        signals = []
        for channel in channels:
            try:
               samples = self.data.get(channel['Name'], channel['Group'])
               df = DataFrame({channel['Name']:samples.samples}, index=to_timedelta(samples.timestamps, unit='s'))
               signals.append(df)
               print(channel['Name'])
               print(df)
            except Exception as e:
                print("Error appending signal {} from group {} ({})".format(channel['Name'], channel['Group'], str(e)))
        if signals:
            print("Resample at {}s".format(resample))
            result = concat(signals, axis=1).resample(rule=str(resample)+'s').mean().ffill()
            result.index.name = 'Time[s]'
            result.index = result.index.total_seconds()
            result.index = (result.index - result.index[0]).round(2)
            # result.index.name = "Time[s]"
            return result

def toName(signalObj:dict):
    """
    Provided a `signalObj`, returns a formatted string in the format `Channel_Name`[`Channel_Unit`]
    """
    return signalObj['Name']+'['+signalObj['Unit']+']'
