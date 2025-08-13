#!/usr/bin/env python3
"""
This module contains classes to call the Cisco support APIs.
Its a deviation from https://github.com/rothdennis/cisco_support as this repo seems not to be updated anymore.

The classes are ordered as followed:
- SNI (Serial Number Information)
- EOX End-of-Life Information
- SS (Software Suggestion)
- ASD (Automated Software Distribution)
- Bug (Software Bug)
- Case (TAC Support Case)
- PI (Product Information)
- RMA (Service Order Return)
"""

import requests

#### Constants ##############################################################################################


# Set the requests timeout for connect and read separatly
REQUESTS_TIMEOUT = (3.05, 27)


#### Utils ##################################################################################################


def get_cisco_support_token(client_id: str, client_secret: str, verify: bool, proxies: dict) -> str:
    """
    Get Cisco Support API Token
    """
    url = "https://id.cisco.com/oauth2/default/v1/token"
    params = {"grant_type": "client_credentials", "client_id": client_id, "client_secret": client_secret}
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    response = requests.post(
        url=url, params=params, headers=headers, verify=verify, proxies=proxies, timeout=REQUESTS_TIMEOUT
    )

    return response.json()["access_token"]


#### Serial Number Information ##############################################################################


class SNI:
    """
    Serial Number Information
    """

    __headers = None
    __verify = None
    __proxies = None

    def __init__(self, key: str, secret: str, verify: bool = True, proxies: dict = None) -> None:
        """
        Class init function
        """
        self.__verify = verify
        self.__proxies = proxies

        token = get_cisco_support_token(key, secret, verify, proxies)

        self.__headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}

    def getCoverageStatusBySerialNumbers(self, sr_no: list) -> dict:
        """
        Get Coverage Status by Serial Numbers
        """
        params = {}

        sr_no = ",".join(sr_no)

        url = f"https://apix.cisco.com/sn2info/v2/coverage/status/serial_numbers/{sr_no}"

        response = requests.get(
            url=url,
            headers=self.__headers,
            params=params,
            verify=self.__verify,
            proxies=self.__proxies,
            timeout=REQUESTS_TIMEOUT,
        )

        return response.json()

    def getCoverageSummaryByInstanceNumbers(self, instance_no: list, page_index: int = 1) -> dict:
        """
        Get Coverage Summary by Instance Numbers
        """
        params = {"page_index": page_index}

        instance_no = ",".join(instance_no)

        url = f"https://apix.cisco.com/sn2info/v2/coverage/summary/instance_numbers/{instance_no}"

        response = requests.get(
            url=url,
            headers=self.__headers,
            params=params,
            verify=self.__verify,
            proxies=self.__proxies,
            timeout=REQUESTS_TIMEOUT,
        )

        return response.json()

    def getCoverageSummaryBySerialNumbers(self, sr_no: list, page_index: int = 1) -> dict:
        """
        Get Coverage Summary by Serial Numbers
        """
        params = {"page_index": page_index}

        sr_no = ",".join(sr_no)

        url = f"https://apix.cisco.com/sn2info/v2/coverage/summary/serial_numbers/{sr_no}"

        response = requests.get(
            url=url,
            headers=self.__headers,
            params=params,
            verify=self.__verify,
            proxies=self.__proxies,
            timeout=REQUESTS_TIMEOUT,
        )

        return response.json()

    def getOrderableProductIDsBySerialNumbers(self, sr_no: list) -> dict:
        """
        Get Orderable Pruduct ID by Serial Numbers
        """
        params = {}

        sr_no = ",".join(sr_no)

        url = f"https://apix.cisco.com/sn2info/v2/identifiers/orderable/serial_numbers/{sr_no}"

        response = requests.get(
            url=url,
            headers=self.__headers,
            params=params,
            verify=self.__verify,
            proxies=self.__proxies,
            timeout=REQUESTS_TIMEOUT,
        )

        return response.json()

    def getOwnerCoverageStatusBySerialNumbers(self, sr_no: list) -> dict:
        """
        Get Owner Coverage Status by Serial Numbers
        """
        params = {}

        sr_no = ",".join(sr_no)

        url = f"https://apix.cisco.com/sn2info/v2/coverage/owner_status/serial_numbers/{sr_no}"

        response = requests.get(
            url=url,
            headers=self.__headers,
            params=params,
            verify=self.__verify,
            proxies=self.__proxies,
            timeout=REQUESTS_TIMEOUT,
        )

        return response.json()


#### End-of-Life Information ################################################################################


class EOX:
    """
    End-of-Life Information
    """

    __headers = None
    __verify = None
    __proxies = None

    def __init__(self, key: str, secret: str, verify: bool = True, proxies: dict = None) -> None:
        """
        Class init function
        """
        self.__verify = verify
        self.__proxies = proxies

        token = get_cisco_support_token(key, secret, verify, proxies)

        self.__headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}

    def getByDates(self, startDate: str, endDate: str, pageIndex: int = 1, eoxAttrib: list = []) -> dict:
        """
        Get EoX by Dates

        Args:
            startDate (str): Start date of the date range of records to return in the following format:
                YYYY-MM-DD. For example: 2010-01-01
            endDate (str): End date of the date range of records to return in the following format:
                YYYY-MM-DD. For example: 2010-01-01
            pageIndex (int, optional): Index number of the page to return; a maximum of 50 records per page
                are returned. Defaults to 1.
            eoxAttrib (list, optional): Attribute or attributes of the records to return. Enter multiple
                values separated by commas. Defaults to [].

        Returns:
            dict: {PaginationResponseRecord, EOXRecord}
        """
        params = {"eoxAttrib": ",".join(eoxAttrib), "responseencoding": "json"}

        url = f"https://apix.cisco.com/supporttools/eox/rest/5/EOXByDates/{pageIndex}/{startDate}/{endDate}"

        response = requests.get(
            url=url,
            headers=self.__headers,
            params=params,
            verify=self.__verify,
            proxies=self.__proxies,
            timeout=REQUESTS_TIMEOUT,
        )

        return response.json()

    def getByProductIDs(self, productID: list, pageIndex: int = 1) -> dict:
        """
        Get EOX by Product IDs

        Args:
            productID (list): Product IDs for the products to retrieve from the database. Enter up to 20 PIDs
                eparated by commas. For example: 15216-OADM1-35=,M92S1K9-1.3.3C Note: To enhance search
                capabilities, the Cisco Support Tools allows wildcards with the productIDs parameter.
                A minimum of 3 characters is required. For example, only the following inputs are valid:
                *VPN*, *VPN, VPN*, and VPN. Using wildcards can result in multiple PIDs in the output.
            pageIndex (int, optional): Index number of the page to return; a maximum of 50 records per page
                are returned. Defaults to 1.

        Returns:
            dict: {PaginationResponseRecord, EOXRecord}
        """
        params = {"responseencoding": "json"}

        productID = ",".join(productID)

        url = f"https://apix.cisco.com/supporttools/eox/rest/5/EOXByProductID/{pageIndex}/{productID}"

        response = requests.get(
            url=url,
            headers=self.__headers,
            params=params,
            verify=self.__verify,
            proxies=self.__proxies,
            timeout=REQUESTS_TIMEOUT,
        )

        return response.json()

    def getBySerialNumbers(self, serialNumber: list, pageIndex: int = 1) -> dict:
        """
        Get EOX by Serial Numbers

        Args:
            serialNumber (list): Device serial number or numbers for which to return results. You can enter
                up to 20 serial numbers (each with a maximum length of 40) separated by commas.
            pageIndex (int, optional): Index number of the page to return; a maximum of 50 records per page
                are returned. Defaults to 1.

        Returns:
            dict: {PaginationResponseRecord, EOXRecord}
        """
        params = {"responseencoding": "json"}

        serialNumber = ",".join(serialNumber)

        url = f"https://apix.cisco.com/supporttools/eox/rest/5/EOXBySerialNumber/{pageIndex}/{serialNumber}"

        response = requests.get(
            url=url,
            headers=self.__headers,
            params=params,
            verify=self.__verify,
            proxies=self.__proxies,
            timeout=REQUESTS_TIMEOUT,
        )

        return response.json()

    def getBySoftwareReleaseStrings(self, software: list, pageIndex: int = 1) -> dict:
        """
        Get EOX by Software Release Strings

        Args:
            software (list): String for software release and type of operating system (optional) for the
                requested product. For example: 12.2,IOS You can enter up to 20 software release and
                operating system type combinations. Each combination can return multiple EoX records.
            pageIndex (int, optional): Index number of the page to return. For example, 1 returns the first
                page of the total number of available pages. Defaults to 1.

        Returns:
            dict: {PaginationResponseRecord, EOXRecord}
        """
        params = {"responseencoding": "json"}

        for i, sw in enumerate(software):
            params.update({f"input{i + 1}": sw})

        url = f"https://apix.cisco.com/supporttools/eox/rest/5/EOXBySWReleaseString/{pageIndex}"

        response = requests.get(
            url=url,
            headers=self.__headers,
            params=params,
            verify=self.__verify,
            proxies=self.__proxies,
            timeout=REQUESTS_TIMEOUT,
        )

        return response.json()


#### Software Suggestion ####################################################################################


class SS:
    """
    Software Suggestion
    """

    __headers = None
    __verify = None
    __proxies = None

    def __init__(self, key: str, secret: str, verify: bool = True, proxies: dict = None) -> None:
        """
        Class init function
        """
        self.__verify = verify
        self.__proxies = proxies

        token = get_cisco_support_token(key, secret, verify, proxies)

        self.__headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}

    def getSuggestedReleasesAndImagesByProductIDs(self, productIds: list, pageIndex: int = 1) -> dict:
        """
        Get Suggested Release and Images by Product IDs
        """
        params = {"pageIndex": pageIndex}

        productIds = ",".join(productIds)

        url = f"https://apix.cisco.com/software/suggestion/v2/suggestions/software/productIds/{productIds}"

        response = requests.get(
            url=url,
            headers=self.__headers,
            params=params,
            verify=self.__verify,
            proxies=self.__proxies,
            timeout=REQUESTS_TIMEOUT,
        )

        return response.json()

    def getSuggestedReleasesByProductIDs(self, productIds: list, pageIndex: int = 1) -> dict:
        """
        Get Suggested Release By Product IDs
        """
        params = {"pageIndex": pageIndex}

        productIds = ",".join(productIds)

        url = f"https://apix.cisco.com/software/suggestion/v2/suggestions/releases/productIds/{productIds}"

        response = requests.get(
            url=url,
            headers=self.__headers,
            params=params,
            verify=self.__verify,
            proxies=self.__proxies,
            timeout=REQUESTS_TIMEOUT,
        )

        return response.json()

    def getCompatibleAndSuggestedSoftwareReleasesByProductID(
        self,
        productId: str,
        currentImage: str = None,
        currentRelease: str = None,
        pageIndex: int = 1,
        supportedFeatures: list = None,
        supportedHardware: list = None,
    ) -> dict:
        """
        Get Compatible and Suggested Software Release by Product ID
        """

        if supportedHardware:
            supportedHardware = "/".join(supportedHardware)
        else:
            supportedHardware = None

        if supportedFeatures:
            supportedFeatures = ",".join(supportedFeatures)
        else:
            supportedFeatures = None

        params = {
            "currentImage": currentImage,
            "currentRelease": currentRelease,
            "supportedFeatures": supportedFeatures,
            "supportedHardware": supportedHardware,
            "pageIndex": pageIndex,
        }

        url = f"https://apix.cisco.com/software/suggestion/v2/suggestions/compatible/productId/{productId}"

        response = requests.get(
            url=url,
            headers=self.__headers,
            params=params,
            verify=self.__verify,
            proxies=self.__proxies,
            timeout=REQUESTS_TIMEOUT,
        )

        return response.json()

    def getSuggestedReleasesAndImagesByMDFIDs(self, mdfIds: list, pageIndex: int = 1) -> dict:
        """
        Get Suggested Release and Images by MDFIDs
        """
        params = {"pageIndex": pageIndex}

        mdfIds = ",".join(mdfIds)

        url = f"https://apix.cisco.com/software/suggestion/v2/suggestions/software/mdfIds/{mdfIds}"

        response = requests.get(
            url=url,
            headers=self.__headers,
            params=params,
            verify=self.__verify,
            proxies=self.__proxies,
            timeout=REQUESTS_TIMEOUT,
        )

        return response.json()

    def getSuggestedReleasesByMDFIDs(self, mdfIds: list, pageIndex: int = 1) -> dict:
        """
        Get Suggested Release by MDFIDs
        """
        params = {"pageIndex": pageIndex}

        mdfIds = ",".join(mdfIds)

        url = f"https://apix.cisco.com/software/suggestion/v2/suggestions/releases/mdfIds/{mdfIds}"

        response = requests.get(
            url=url,
            headers=self.__headers,
            params=params,
            verify=self.__verify,
            proxies=self.__proxies,
            timeout=REQUESTS_TIMEOUT,
        )

        return response.json()

    def getCompatibleAndSuggestedSoftwareReleasesByMDFID(
        self,
        mdfId: str,
        currentImage: str = None,
        currentRelease: str = None,
        pageIndex: int = 1,
        supportedFeatures: list = None,
        supportedHardware: list = None,
    ) -> dict:
        """
        Get Compatible and Suggested Software Release by MDFID
        """

        if supportedHardware:
            supportedHardware = "/".join(supportedHardware)
        else:
            supportedHardware = None

        if supportedFeatures:
            supportedFeatures = ",".join(supportedFeatures)
        else:
            supportedFeatures = None

        params = {
            "pageIndex": pageIndex,
            "currentImage": currentImage,
            "currentRelease": currentRelease,
            "supportedFeatures": supportedFeatures,
            "supportedHardware": supportedHardware,
        }

        url = f"https://apix.cisco.com/software/suggestion/v2/suggestions/compatible/mdfId/{mdfId}"

        response = requests.get(
            url=url,
            headers=self.__headers,
            params=params,
            verify=self.__verify,
            proxies=self.__proxies,
            timeout=REQUESTS_TIMEOUT,
        )

        return response.json()


#### Automated Software Distribution ########################################################################


class ASD:
    """
    Automated Software Distribution
    """

    __headers = None
    __verify = None
    __proxies = None

    def __init__(self, key: str, secret: str, verify: bool = True, proxies: dict = None) -> None:
        """
        Class init function
        """
        self.__verify = verify
        self.__proxies = proxies

        token = get_cisco_support_token(key, secret, verify, proxies)

        self.__headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def getByProductIDAndRelease(
        self,
        pid: str,
        currentReleaseVersion: str,
        outputReleaseVersion: str = "latest",
        pageIndex: int = 1,
        perPage: int = 25,
    ) -> dict:
        """
        Get Release by Product ID and Release
        """
        data = {
            "pid": pid,
            "currentReleaseVersion": currentReleaseVersion,
            "outputReleaseVersion": outputReleaseVersion,
            "pageIndex": pageIndex,
            "perPage": perPage,
        }

        url = "https://apix.cisco.com/software/v4.0/metadata/pidrelease"

        response = requests.post(
            url=url,
            params=data,
            headers=self.__headers,
            verify=self.__verify,
            proxies=self.__proxies,
            timeout=REQUESTS_TIMEOUT,
        )

        return response.json()

    def getByProductIDAndImage(self) -> dict:
        """
        Get by Product ID and Image
        """


#### Bug ####################################################################################################


class Bug:
    """
    Bug
    """

    __headers = None
    __verify = None
    __proxies = None

    def __init__(self, key: str, secret: str, verify: bool = True, proxies: dict = None) -> None:
        """
        Class Init Function
        """
        self.__verify = verify
        self.__proxies = proxies
        self.baseurl = "https://apix.cisco.com/bug/v2.0/bugs"

        token = get_cisco_support_token(key, secret, verify, proxies)

        self.__headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}

    def getByIDs(self, bug_ids: list) -> dict:
        """
        Get Bug by IDs
        """
        params = {}

        bug_ids = ",".join(bug_ids)

        url = f"{self.baseurl}/bug_ids/{bug_ids}"

        response = requests.get(
            url=url,
            headers=self.__headers,
            params=params,
            verify=self.__verify,
            proxies=self.__proxies,
            timeout=REQUESTS_TIMEOUT,
        )

        return response.json()

    def getByBaseProductIDs(
        self,
        base_pid: str,
        page_index: int = 1,
        status: str = None,
        modified_date: str = 2,
        severity: str = None,
        sort_by: str = None,
    ) -> dict:
        """
        Get Bug by Base Product IDS
        """
        params = {
            "page_index": page_index,
            "modified_date": modified_date,
            "status": status,
            "severity": severity,
            "sort_by": sort_by,
        }

        url = f"{self.baseurl}/products/product_id/{base_pid}"

        response = requests.get(
            url=url,
            headers=self.__headers,
            params=params,
            verify=self.__verify,
            proxies=self.__proxies,
            timeout=REQUESTS_TIMEOUT,
        )

        return response.json()

    def getByBaseProductIDsAndSoftwareReleases(
        self,
        base_pid: str,
        software_releases: str,
        page_index: int = 1,
        status: str = None,
        modified_date: str = 2,
        severity: str = None,
        sort_by: str = None,
    ) -> dict:
        """
        Get Bug by Base Pruduct IDs and Software Release
        """
        params = {
            "page_index": page_index,
            "modified_date": modified_date,
            "status": status,
            "severity": severity,
            "sort_by": sort_by,
        }

        url = f"{self.baseurl}/products/product_id/{base_pid}/software_releases/{software_releases}"

        response = requests.get(
            url=url,
            headers=self.__headers,
            params=params,
            verify=self.__verify,
            proxies=self.__proxies,
            timeout=REQUESTS_TIMEOUT,
        )

        return response.json()

    def getByKeywords(
        self,
        keyword: list,
        page_index: int = 1,
        status: str = None,
        modified_date: str = 2,
        severity: str = None,
        sort_by: str = None,
    ) -> dict:
        """
        Get Bug by Keywords
        """
        params = {
            "page_index": page_index,
            "modified_date": modified_date,
            "status": status,
            "severity": severity,
            "sort_by": sort_by,
        }

        keyword = ",".join(keyword)

        url = f"{self.baseurl}/keyword/{keyword}"

        response = requests.get(
            url=url,
            headers=self.__headers,
            params=params,
            verify=self.__verify,
            proxies=self.__proxies,
            timeout=REQUESTS_TIMEOUT,
        )

        return response.json()

    def getByProductSeriesAndAffectedSoftwareRelease(
        self,
        product_series: str,
        affected_releases: list,
        page_index: int = 1,
        status: str = None,
        modified_date: str = None,
        severity: str = None,
        sort_by: str = None,
    ) -> dict:
        """
        Get Bug by Product Series and Affected Software Release
        """
        affected_releases = ",".join(affected_releases)

        params = {
            "page_index": page_index,
            "modified_date": modified_date,
            "status": status,
            "severity": severity,
            "sort_by": sort_by,
        }

        url = f"{self.baseurl}/product_series/{product_series}/affected_releases/{affected_releases}"

        response = requests.get(
            url=url,
            headers=self.__headers,
            params=params,
            verify=self.__verify,
            proxies=self.__proxies,
            timeout=REQUESTS_TIMEOUT,
        )

        return response.json()

    def getByProductSeriesAndFixedInSoftwareRelease(
        self,
        product_series: str,
        fixed_in_releases: list,
        page_index: str = 1,
        status: str = None,
        modified_date: str = 2,
        severity: str = None,
        sort_by: str = None,
    ) -> dict:
        """
        Get Bug by Product Series and Fixed in Software Release
        """
        fixed_in_releases = ",".join(fixed_in_releases)

        params = {
            "page_index": page_index,
            "modified_date": modified_date,
            "status": status,
            "severity": severity,
            "sort_by": sort_by,
        }

        url = f"{self.baseurl}/product_series/{product_series}/fixed_in_releases/{fixed_in_releases}"

        response = requests.get(
            url=url,
            headers=self.__headers,
            params=params,
            verify=self.__verify,
            proxies=self.__proxies,
            timeout=REQUESTS_TIMEOUT,
        )

        return response.json()

    def getByProductNameAndAffectedSoftwareRelease(
        self,
        product_name: str,
        affected_releases: list,
        page_index: str = 1,
        status: str = None,
        modified_date: str = 2,
        severity: str = None,
        sort_by: str = None,
    ) -> dict:
        """
        Get Bug by Product Name and Affected Software Release
        """
        affected_releases = ",".join(affected_releases)

        params = {
            "page_index": page_index,
            "modified_date": modified_date,
            "status": status,
            "severity": severity,
            "sort_by": sort_by,
        }

        url = f"{self.baseurl}/product_name/{product_name}/affected_releases/{affected_releases}"

        response = requests.get(
            url=url,
            headers=self.__headers,
            params=params,
            verify=self.__verify,
            proxies=self.__proxies,
            timeout=REQUESTS_TIMEOUT,
        )

        return response.json()

    def getByProductNameAndFixedInSoftwareRelease(
        self,
        product_name: str,
        fixed_in_releases: list,
        page_index: str = 1,
        status: str = None,
        modified_date: str = 2,
        severity: str = None,
        sort_by: str = None,
    ) -> dict:
        """
        Get Bug by Product Name and Fixed In Software Release
        """
        fixed_in_releases = ",".join(fixed_in_releases)

        params = {
            "page_index": page_index,
            "modified_date": modified_date,
            "status": status,
            "severity": severity,
            "sort_by": sort_by,
        }

        url = f"{self.baseurl}/product_name/{product_name}/fixed_in_releases/{fixed_in_releases}"

        response = requests.get(
            url=url,
            headers=self.__headers,
            params=params,
            verify=self.__verify,
            proxies=self.__proxies,
            timeout=REQUESTS_TIMEOUT,
        )

        return response.json()


#### Case ###################################################################################################


class Case:
    """
    Case
    """

    __headers = None
    __verify = None
    __proxies = None

    def __init__(self, key: str, secret: str, verify: bool = True, proxies: dict = None) -> None:
        """
        Class Init Function
        """
        self.__verify = verify
        self.__proxies = proxies

        token = get_cisco_support_token(key, secret, verify, proxies)

        self.__headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }

    def getCaseSummary(self, case_ids: list, sort_by: str = "UPDATED_DATE") -> dict:
        """
        Get Case Summary
        """
        params = {"sort_by": sort_by}

        case_ids = ",".join(case_ids)

        url = f"https://apix.cisco.com/case/v3/cases/case_ids/{case_ids}"

        response = requests.get(
            url=url,
            headers=self.__headers,
            params=params,
            verify=self.__verify,
            proxies=self.__proxies,
            timeout=REQUESTS_TIMEOUT,
        )

        return response.json()

    def getCaseDetails(self, case_id: str) -> dict:
        """
        Get Case Details
        """
        params = {}

        url = f"https://apix.cisco.com/case/v3/cases/details/case_id/{case_id}"

        response = requests.get(
            url=url,
            headers=self.__headers,
            params=params,
            verify=self.__verify,
            proxies=self.__proxies,
            timeout=REQUESTS_TIMEOUT,
        )

        return response.json()

    def getByContractID(
        self,
        contract_ids: list,
        date_created_from: str,
        date_created_to: str,
        status_flag: str = "O",
        sort_by: str = "UPDATED_DATE",
        page_index: int = 1,
    ) -> dict:
        """
        Get Case by Contract ID
        """
        params = {
            "date_created_from": date_created_from,
            "date_created_to": date_created_to,
            "sort_by": sort_by,
            "status_flag": status_flag,
            "page_index": page_index,
        }

        contract_ids = ",".join(contract_ids)

        url = f"https://apix.cisco.com/case/v3/cases/contracts/contract_ids/{contract_ids}"

        response = requests.get(
            url=url,
            headers=self.__headers,
            params=params,
            verify=self.__verify,
            proxies=self.__proxies,
            timeout=REQUESTS_TIMEOUT,
        )

        return response.json()

    def getByUserID(
        self,
        user_ids: list,
        date_created_from: str = None,
        date_created_to: str = None,
        status_flag: str = "O",
        sort_by: str = "UPDATED_DATE",
        page_index: int = 1,
    ) -> dict:
        """
        Get Case by User ID
        """
        params = {
            "date_created_from": date_created_from,
            "date_created_to": date_created_to,
            "sort_by": sort_by,
            "status_flag": status_flag,
            "page_index": page_index,
        }

        user_ids = ",".join(user_ids)

        url = f"https://apix.cisco.com/case/v3/cases/users/user_ids/{user_ids}"

        response = requests.get(
            url=url,
            headers=self.__headers,
            params=params,
            verify=self.__verify,
            proxies=self.__proxies,
            timeout=REQUESTS_TIMEOUT,
        )

        return response.json()


#### Product Information ####################################################################################


class PI:
    """
    Product Information
    """

    __headers = None
    __verify = None
    __proxies = None

    def __init__(self, key: str, secret: str, verify: bool = True, proxies: dict = None) -> None:
        """
        Class Init Function
        """
        self.__verify = verify
        self.__proxies = proxies

        token = get_cisco_support_token(key, secret, verify, proxies)

        self.__headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}

    def getBySerialNumbers(self, serial_numbers: list, page_index: int = 1) -> dict:
        """
        Get Product Information by Serial Numbers
        """
        params = {"page_index": page_index}

        serial_numbers = ",".join(serial_numbers)

        url = f"https://apix.cisco.com/product/v1/information/serial_numbers/{serial_numbers}"

        response = requests.get(
            url=url,
            headers=self.__headers,
            params=params,
            verify=self.__verify,
            proxies=self.__proxies,
            timeout=REQUESTS_TIMEOUT,
        )

        return response.json()

    def getByProductIDs(self, product_ids: list, page_index: int = 1) -> dict:
        """
        Get Product Information by Product IDs
        """
        params = {"page_index": page_index}

        product_ids = ",".join(product_ids)

        url = f"https://apix.cisco.com/product/v1/information/product_ids/{product_ids}"

        response = requests.get(
            url=url,
            headers=self.__headers,
            params=params,
            verify=self.__verify,
            proxies=self.__proxies,
            timeout=REQUESTS_TIMEOUT,
        )

        return response.json()

    def getMDFInformationByProductIDs(self, product_ids: list, page_index: int = 1) -> dict:
        """
        Get Product Information by Product IDs
        """
        params = {"page_index": page_index}

        product_ids = ",".join(product_ids)

        url = f"https://apix.cisco.com/product/v1/information/product_ids/{product_ids}"

        response = requests.get(
            url=url,
            headers=self.__headers,
            params=params,
            verify=self.__verify,
            proxies=self.__proxies,
            timeout=REQUESTS_TIMEOUT,
        )

        return response.json()


#### RMA ####################################################################################################


class RMA:
    """
    RMA
    """

    __headers = None
    __verify = None
    __proxies = None

    def __init__(self, key: str, secret: str, verify: bool = True, proxies: dict = None) -> None:
        """
        Class Init Function
        """
        self.__verify = verify
        self.__proxies = proxies

        token = get_cisco_support_token(key, secret, verify, proxies)

        self.__headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}

    def getByRMANumber(self, rma_numbers: str) -> dict:
        """
        Get RMA by RMA Number
        """
        params = {}

        url = f"https://apix.cisco.com/return/v1.0/returns/rma_numbers/{rma_numbers}"

        response = requests.get(
            url=url,
            headers=self.__headers,
            params=params,
            verify=self.__verify,
            proxies=self.__proxies,
            timeout=REQUESTS_TIMEOUT,
        )

        return response.json()

    def getByUserID(
        self,
        user_ids: str,
        fromDate: str = None,
        toDate: str = None,
        status: str = None,
        sortBy: str = "orderdate",
    ) -> dict:
        """
        Get RMA by User IS
        """
        params = {"fromDate": fromDate, "toDate": toDate, "status": status, "sortBy": sortBy}

        url = f"https://apix.cisco.com/return/v1.0/returns/users/user_ids/{user_ids}"

        response = requests.get(
            url=url,
            headers=self.__headers,
            params=params,
            verify=self.__verify,
            proxies=self.__proxies,
            timeout=REQUESTS_TIMEOUT,
        )

        return response.json()
