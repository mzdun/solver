import sys
sys.path.append("../solver")
from os import path
from IniReader import *
from xml.dom import minidom
import uuid
from files import FileList

def print_filter(out, files, name, root, keys, base = ""):
    if len(keys) == 0: return
    print >>out, "  <ItemGroup>"
    for k in keys:
        p = files.sec.items[k].name
        f = "\\".join(path.split(p)[0].split("/"))
        f = "%s%s" % (base, f)
        p = "%s%s" % (root, p)
        p = "\\".join(p.split("/"))
        if f == "":
            print >>out, """    <%s Include="%s" />""" % (name, p)
        else:
            print >>out, """    <%s Include="%s">
      <Filter>%s</Filter>
    </%s>""" % (name, p, f, name)
    print >>out, "  </ItemGroup>"

def print_file(out, files, name, root, keys):
    if len(keys) == 0: return
    print >>out, "  <ItemGroup>"
    for k in keys:
        p = "%s%s" % (root, files.sec.items[k].name)
        p = "\\".join(p.split("/"))
        if k in files.cfiles:
            print >>out, """    <%s Include="%s">
      <PrecompiledHeader>NotUsing</PrecompiledHeader>
    </%s>""" % (name, p, name)
        elif k in files.cppfiles and "pch:1" in files.sec.items[k].value:
            print >>out, """    <%s Include="%s">
      <PrecompiledHeader>Create</PrecompiledHeader>
    </%s>""" % (name, p, name)
        else:
            print >>out, """    <%s Include="%s" />""" % (name, p)
    print >>out, "  </ItemGroup>"

def print_filters(files, outname, root):
    if files.file_fresh(outname): return
    print outname
    out = open(outname, "w")
    dirs = {}
    for f in files.sec.items:
        base = ""
        if f in files.includes: base = "Header Files\\"
        elif (f in files.cfiles) or (f in files.cppfiles): base = "Source Files\\"
        else: base = "Resource Files\\"
        p = path.split(files.sec.items[f].name)[0]
        while p != "":
            dirs["%s%s" % (base, "\\".join(p.split("/")))] = 1
            p = path.split(p)[0]

    print >>out, """<?xml version=\"1.0\" encoding=\"utf-8\"?>
    <Project ToolsVersion="4.0" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
      <ItemGroup>
    <Filter Include="Source Files">
      <UniqueIdentifier>{4FC737F1-C7A5-4376-A066-2A32D752A2FF}</UniqueIdentifier>
      <Extensions>cpp;c;cc;cxx;def;odl;idl;hpj;bat;asm;asmx</Extensions>
    </Filter>
    <Filter Include="Header Files">
      <UniqueIdentifier>{93995380-89BD-4b04-88EB-625FBE52EBFB}</UniqueIdentifier>
      <Extensions>h;hpp;hxx;hm;inl;inc;xsd</Extensions>
    </Filter>
    <Filter Include="Resource Files">
      <UniqueIdentifier>{67DA6AB6-F800-4c08-8B7A-83BB121AAD01}</UniqueIdentifier>
      <Extensions>rc;ico;cur;bmp;dlg;rc2;rct;bin;rgs;gif;jpg;jpeg;jpe;resx;tiff;tif;png;wav;mfcribbon-ms</Extensions>
    </Filter>"""
    dirs = dirs.keys()
    dirs.sort()
    for d in dirs:
        print >>out, """    <Filter Include=\"%s\">
      <UniqueIdentifier>{%s}</UniqueIdentifier>
    </Filter>""" % (d, uuid.uuid1())
    print >>out, "  </ItemGroup>"
    print_filter(out, files, "None", root, files.datafiles, "Resource Files\\")
    print_filter(out, files, "ClCompile", root, files.cfiles + files.cppfiles, "Source Files\\")
    print_filter(out, files, "ClInclude", root, files.includes, "Header Files\\")
    print >>out, "</Project>"

def print_project(files, outname, root, bintype, basename, guid):
    if files.file_fresh(outname): return
    print outname
    out = open(outname, "w")
    print >>out, """<?xml version="1.0" encoding="utf-8"?>
<Project DefaultTargets="Build" ToolsVersion="4.0" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
  <ItemGroup Label="ProjectConfigurations">
    <ProjectConfiguration Include="Debug|Win32">
      <Configuration>Debug</Configuration>
      <Platform>Win32</Platform>
    </ProjectConfiguration>
    <ProjectConfiguration Include="Debug|x64">
      <Configuration>Debug</Configuration>
      <Platform>x64</Platform>
    </ProjectConfiguration>
    <ProjectConfiguration Include="Release|Win32">
      <Configuration>Release</Configuration>
      <Platform>Win32</Platform>
    </ProjectConfiguration>
    <ProjectConfiguration Include="Release|x64">
      <Configuration>Release</Configuration>
      <Platform>x64</Platform>
    </ProjectConfiguration>
  </ItemGroup>
  <PropertyGroup Label="Globals">
    <ProjectGuid>{%s}</ProjectGuid>
    <Keyword>Win32Proj</Keyword>
    <RootNamespace>%s</RootNamespace>
  </PropertyGroup>
  <Import Project="$(VCTargetsPath)\Microsoft.Cpp.Default.props" />
  <PropertyGroup Label="Configuration">
    <ConfigurationType>%s</ConfigurationType>
    <CharacterSet>Unicode</CharacterSet>
  </PropertyGroup>
  <PropertyGroup Condition="'$(Configuration)'=='Debug'" Label="Configuration">
    <UseDebugLibraries>true</UseDebugLibraries>
  </PropertyGroup>
  <PropertyGroup Condition="'$(Configuration)'=='Release'" Label="Configuration">
    <UseDebugLibraries>false</UseDebugLibraries>
    <WholeProgramOptimization>true</WholeProgramOptimization>
  </PropertyGroup>
  <Import Project="$(VCTargetsPath)\Microsoft.Cpp.props" />
  <ImportGroup Label="ExtensionSettings">
  </ImportGroup>
  <ImportGroup Label="PropertySheets">
    <Import Project="$(SolutionDir)\Solver.props" Condition="exists('$(SolutionDir)\Solver.props')" />
    <Import Project="$(SolutionDir)\Solver.%s.props" Condition="exists('$(SolutionDir)\Solver.%s.props')" />
    <Import Project="$(SolutionDir)\Solver.$(Platform).props" Condition="exists('$(SolutionDir)\Solver.$(Platform).props')" />
    <Import Project="$(SolutionDir)\Solver.$(Configuration).props" Condition="exists('$(SolutionDir)\Solver.$(Configuration).props')" />
    <Import Project="$(SolutionDir)\Solver.$(Platform).$(Configuration).props" Condition="exists('$(SolutionDir)\Solver.$(Platform).$(Configuration).props')" />
  </ImportGroup>
  <PropertyGroup Label="UserMacros" />""" % (guid, basename, bintype, basename, basename)
    print_file(out, files, "None", root, files.datafiles)
    print_file(out, files, "ClCompile", root, files.cfiles + files.cppfiles)
    print_file(out, files, "ClInclude", root, files.includes)
    print >>out, """  <Import Project="$(VCTargetsPath)\Microsoft.Cpp.targets" />
  <ImportGroup Label="ExtensionTargets">
  </ImportGroup>
</Project>"""

    
def create_project(root, base, bintype, guid):
    files = FileList()
    predef = Macros()
    predef.add_macro("WIN32", "", Location("<command-line>", 0))
    files.read(predef, "%splatforms/%s.files" % (root, base))
    print_filters(files, "%s.vcxproj.filters" % base, root)
    print_project(files, "%s.vcxproj" % base, root, bintype, base, guid)

create_project(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
