using ProjectEmokit.Helpers;
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ProjectEmokit.Python
{
    public class PythonProcesses
    {
        public Process myProcess { get; set; }
        public void StartPythonEEG(string arguments)
        {
            myProcess = new Process();
            myProcess.StartInfo.FileName = StaticVariables.COMMAND_PROMPT;
            Console.WriteLine("Python process initialized");

            myProcess.StartInfo.UseShellExecute = false;
            myProcess.StartInfo.Arguments = StaticVariables.PYTHON_EEG + arguments;
            myProcess.StartInfo.Verb = "runas";

            // start the process 
            myProcess.Start();
        }
        
        public void EndPythonEEG()
        {
            myProcess.Close();
        }
    }
}
