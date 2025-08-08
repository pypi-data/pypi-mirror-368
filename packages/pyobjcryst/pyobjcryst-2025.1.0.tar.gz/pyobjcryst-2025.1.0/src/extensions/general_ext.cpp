/*****************************************************************************
*
* pyobjcryst        by DANSE Diffraction group
*                   Simon J. L. Billinge
*                   (c) 2009 The Trustees of Columbia University
*                   in the City of New York.  All rights reserved.
*
* File coded by:    Chris Farrow
*
* See AUTHORS.txt for a list of people who contributed.
* See LICENSE_DANSE.txt for license information.
*
******************************************************************************
*
* boost::python bindings to general structures and objects defined in
* ObjCryst/ObjCryst/General.h
*
*****************************************************************************/

#include <boost/python/def.hpp>
#include <boost/python/dict.hpp>
#include <boost/python/enum.hpp>

#include <ObjCryst/version.h>
#include <ObjCryst/ObjCryst/General.h>

#if LIBOBJCRYST_VERSION < 2017002002000LL
#error pyobjcryst requires libobjcryst 2017.2.2 or later.
#endif

using namespace boost::python;
using namespace ObjCryst;

// wrappers ------------------------------------------------------------------

namespace {

const char* doc__get_libobjcryst_version_info_dict = "\
Return dictionary with version data for the loaded libobjcryst library.\n\
";

dict get_libobjcryst_version_info_dict()
{
    dict rv;
    rv["version"] = libobjcryst_version_info::version;
    rv["version_str"] = libobjcryst_version_info::version_str;
    rv["major"] = libobjcryst_version_info::major;
    rv["minor"] = libobjcryst_version_info::minor;
    rv["micro"] = libobjcryst_version_info::micro;
    rv["date"] = libobjcryst_version_info::date;
    rv["git_commit"] = libobjcryst_version_info::git_commit;
    rv["patch"] = libobjcryst_version_info::patch;
    return rv;
}

}   // namespace

// ---------------------------------------------------------------------------

void wrap_general()
{
    enum_<RadiationType>("RadiationType")
        .value("RAD_NEUTRON", RAD_NEUTRON)
        .value("RAD_XRAY", RAD_XRAY)
        .value("RAD_ELECTRON", RAD_ELECTRON)
        ;

    // Only import wavelength types actually used
    enum_<WavelengthType>("WavelengthType")
        .value("WAVELENGTH_MONOCHROMATIC", WAVELENGTH_MONOCHROMATIC)
        .value("WAVELENGTH_ALPHA12", WAVELENGTH_ALPHA12)
        .value("WAVELENGTH_TOF", WAVELENGTH_TOF)
        ;

    def("_get_libobjcryst_version_info_dict",
            get_libobjcryst_version_info_dict,
            doc__get_libobjcryst_version_info_dict);
}
