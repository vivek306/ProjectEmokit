using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ProjectEmokit.Helpers
{
    class StaticVariables
    {
        public static void Get_PYTHON_EEG_PATH()
        {
            string path = AppDomain.CurrentDomain.BaseDirectory;
            // Navigate to the python project location
            path = path.Replace(@"ProjectEmokit\bin\Debug\", "Emokit.EEG");
            PYTHON_EEG_PATH = path;
        }

        public static void SetStaticVariables()
        {
            Get_PYTHON_EEG_PATH();
            DECRYPT_EEG_PATH = PYTHON_EEG_PATH + @"\eeg";
            EEG_APP = @"""" + PYTHON_EEG_PATH + @"\Emokit.EEG.py""";
            PYTHON_EEG = "/K " + PYTHON_APP + " -i " + EEG_APP;
        }

        // Python Commands
        public static string COMMAND_PROMPT = "cmd.exe";
        public static string PYTHON_APP = @"C:\Python27\python.exe";
        public static string PYTHON_EEG_PATH = "";
        public static string DECRYPT_EEG_PATH = "";
        public static string EEG_APP = "";
        public static string PYTHON_EEG = "";

        // Server URL
        public static string ServerURL = "http://localhost:51560/signalr";
        public static string EmokitHub = "EmokitHub";
    }
}
